from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import Http404
import os

from .forms import TeamForm, ExperimentForm
from .file_storage import (
    create_team, get_team, get_team_experiments, create_experiment, 
    get_experiment, save_measurements, get_measurements, save_results, get_results
)
from .utils import analyze_data
from django.conf import settings

def get_admin_password():
    password_file = os.path.join(settings.BASE_DIR, 'admin_password.ps')
    try:
        with open(password_file, 'r') as f:
            return f.read().strip()
    except Exception as e:
        return "admin123"  # Значение по умолчанию, если файл не найден

def index(request):
    return render(request, 'experiment/index.html')

def create_team_view(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = create_team(form.cleaned_data['name'])
            messages.success(request, f'Команда "{team["name"]}" создана!')
            return redirect(reverse('team_experiments', kwargs={'team_id': team['id']}))
    else:
        form = TeamForm()
    
    return render(request, 'experiment/create_team.html', {'form': form})

def find_team_view(request):
    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        team = get_team(name=team_name)
        if team:
            return redirect(reverse('team_experiments', kwargs={'team_id': team['id']}))
        else:
            messages.error(request, 'Команда с таким названием не найдена.')
    
    return render(request, 'experiment/find_team.html')

def team_experiments_view(request, team_id):
    team = get_team(team_id=int(team_id))
    if not team:
        raise Http404("Команда не найдена")
    
    experiments = get_team_experiments(team['name'])
    
    return render(request, 'experiment/team_experiments.html', {
        'team': team,
        'experiments': experiments,
    })

def create_experiment_view(request, team_id):
    team = get_team(team_id=int(team_id))
    if not team:
        raise Http404("Команда не найдена")
    
    if request.method == 'POST':
        form = ExperimentForm(request.POST)
        if form.is_valid():
            experiment = create_experiment(team['name'], form.cleaned_data['title'])
            return redirect(reverse('edit_experiment', kwargs={'experiment_id': experiment['id']}))
    else:
        form = ExperimentForm()
    
    return render(request, 'experiment/create_experiment.html', {
        'form': form,
        'team': team,
    })

def edit_experiment_view(request, experiment_id):
    experiment_id = int(experiment_id)
    
    teams = get_team()
    experiment = None
    team_name = None
    team_id = None
    
    for team in teams:
        experiments = get_team_experiments(team['name'])
        for exp in experiments:
            if exp['id'] == experiment_id:
                experiment = exp
                team_name = team['name']
                team_id = team['id']
                break
        if experiment:
            break
    
    if not experiment:
        raise Http404("Эксперимент не найден")
    
    measurements = get_measurements(team_name, experiment_id)
    
    if request.method == 'POST':
        new_measurements = []
        
        total_forms = int(request.POST.get('measurements-TOTAL_FORMS', 0))
        
        for i in range(total_forms):
            time_key = f'measurements-{i}-time'
            position_key = f'measurements-{i}-position'
            
            if time_key in request.POST and position_key in request.POST:
                try:
                    time = float(request.POST[time_key])
                    position = float(request.POST[position_key])
                    
                    new_measurements.append({
                        'time': time,
                        'position': position
                    })
                except ValueError:
                    pass
        
        new_measurements.sort(key=lambda m: m['time'])
        
        save_measurements(team_name, experiment_id, new_measurements)
        measurements = new_measurements
        
        if 'process' in request.POST:
            if measurements:
                times = [m['time'] for m in measurements]
                positions = [m['position'] for m in measurements]
                
                results = analyze_data(times, positions, experiment_id, team_name)
                save_results(team_name, experiment_id, results)
                
                return redirect(reverse('experiment_results', kwargs={'experiment_id': experiment_id}))
            else:
                messages.warning(request, 'Добавьте точки измерения для анализа.')
        else:
            messages.success(request, 'Точки измерения сохранены!')
    
    experiment['team_id'] = team_id
    
    return render(request, 'experiment/edit_experiment.html', {
        'experiment': experiment,
        'measurements': measurements,
    })

def experiment_results_view(request, experiment_id):
    experiment_id = int(experiment_id)
    
    teams = get_team()
    experiment = None
    team_name = None
    team_id = None
    
    for team in teams:
        experiments = get_team_experiments(team['name'])
        for exp in experiments:
            if exp['id'] == experiment_id:
                experiment = exp
                team_name = team['name']
                team_id = team['id']
                break
        if experiment:
            break
    
    if not experiment:
        raise Http404("Эксперимент не найден")
    
    measurements = get_measurements(team_name, experiment_id)
    results = get_results(team_name, experiment_id)
    
    if not measurements:
        messages.warning(request, 'Добавьте точки измерения для анализа.')
        return redirect(reverse('edit_experiment', kwargs={'experiment_id': experiment_id}))
    
    if not results:
        messages.warning(request, 'Необходимо обработать данные.')
        return redirect(reverse('edit_experiment', kwargs={'experiment_id': experiment_id}))
    
    graph_path = f"/data/{team_name}/{experiment_id}/graph.png"
    
    experiment['team_id'] = team_id
    
    return render(request, 'experiment/experiment_results.html', {
        'experiment': experiment,
        'measurements': measurements,
        'graph_path': graph_path,
    })

def admin_login_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        admin_password = get_admin_password()
        
        if password == admin_password:
            request.session['is_admin'] = True
            return redirect('admin_teams')
        else:
            messages.error(request, 'Неверный пароль администратора')
    
    return render(request, 'experiment/admin_login.html')

def admin_teams_view(request):
    if not request.session.get('is_admin', False):
        messages.error(request, 'Необходимо войти как администратор')
        return redirect('admin_login')
    
    try:
        teams = get_team()
        
        if teams is None:
            teams = []
        
        for team in teams:
            experiments = get_team_experiments(team['name'])
            team['experiments_count'] = len(experiments)
        
        return render(request, 'experiment/admin_teams.html', {
            'teams': teams
        })
    except Exception as e:
        print(f"Ошибка в admin_teams_view: {e}")
        messages.error(request, f'Произошла ошибка: {e}')
        return redirect('index')

def admin_delete_team_view(request, team_id):
    if not request.session.get('is_admin', False):
        messages.error(request, 'Необходимо войти как администратор')
        return redirect('admin_login')
    
    from .file_storage import delete_team
    if delete_team(team_id):
        messages.success(request, 'Команда успешно удалена')
    else:
        messages.error(request, 'Не удалось удалить команду')
    
    return redirect('admin_teams')

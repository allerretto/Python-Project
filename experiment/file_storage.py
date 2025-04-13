import os
import json
import time
from pathlib import Path
from django.conf import settings

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')

def ensure_dir(directory):
    os.makedirs(directory, exist_ok=True)

def get_teams_file():
    ensure_dir(DATA_DIR)
    return os.path.join(DATA_DIR, 'teams.json')

def get_team_dir(team_name):
    team_dir = os.path.join(DATA_DIR, team_name)
    ensure_dir(team_dir)
    return team_dir

def get_experiment_dir(team_name, experiment_id):
    experiment_dir = os.path.join(get_team_dir(team_name), str(experiment_id))
    ensure_dir(experiment_dir)
    return experiment_dir

def load_teams():
    teams_file = get_teams_file()
    if os.path.exists(teams_file):
        with open(teams_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_teams(teams):
    teams_file = get_teams_file()
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)

def create_team(name):
    teams = load_teams()
    
    for team in teams:
        if team['name'] == name:
            return team
    
    team = {
        'id': len(teams) + 1,
        'name': name,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    teams.append(team)
    save_teams(teams)
    
    get_team_dir(name)
    
    return team

def get_team(team_id=None, name=None):
    teams = load_teams()
    
    if team_id is None and name is None:
        return teams
    
    if team_id is not None:
        for team in teams:
            if team['id'] == team_id:
                return team
    
    if name is not None:
        for team in teams:
            if team['name'] == name:
                return team
    
    return None

def get_team_experiments(team_name):
    team_dir = get_team_dir(team_name)
    experiments = []
    
    for item in os.listdir(team_dir):
        experiment_dir = os.path.join(team_dir, item)
        if os.path.isdir(experiment_dir):
            info_file = os.path.join(experiment_dir, 'info.json')
            if os.path.exists(info_file):
                with open(info_file, 'r', encoding='utf-8') as f:
                    experiment = json.load(f)
                    experiments.append(experiment)
    
    experiments.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return experiments

def create_experiment(team_name, title):
    team_dir = get_team_dir(team_name)
    
    experiment_id = 1
    experiments = get_team_experiments(team_name)
    if experiments:
        experiment_id = max(exp.get('id', 0) for exp in experiments) + 1
    
    experiment = {
        'id': experiment_id,
        'title': title,
        'team_name': team_name,
        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'measurements_count': 0,
        'has_results': False
    }
    
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    
    with open(os.path.join(experiment_dir, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(experiment_dir, 'measurements.json'), 'w', encoding='utf-8') as f:
        json.dump([], f)
    
    return experiment

def get_experiment(team_name, experiment_id):
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    info_file = os.path.join(experiment_dir, 'info.json')
    
    if os.path.exists(info_file):
        with open(info_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def save_measurements(team_name, experiment_id, measurements):
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    measurements_file = os.path.join(experiment_dir, 'measurements.json')
    
    with open(measurements_file, 'w', encoding='utf-8') as f:
        json.dump(measurements, f, ensure_ascii=False, indent=2)
    
    info_file = os.path.join(experiment_dir, 'info.json')
    with open(info_file, 'r', encoding='utf-8') as f:
        experiment = json.load(f)
    
    experiment['measurements_count'] = len(measurements)
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2)

def get_measurements(team_name, experiment_id):
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    measurements_file = os.path.join(experiment_dir, 'measurements.json')
    
    if os.path.exists(measurements_file):
        with open(measurements_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return []

def save_results(team_name, experiment_id, results):
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    results_file = os.path.join(experiment_dir, 'results.json')
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    info_file = os.path.join(experiment_dir, 'info.json')
    with open(info_file, 'r', encoding='utf-8') as f:
        experiment = json.load(f)
    
    experiment['has_results'] = True
    experiment['acceleration'] = results.get('acceleration')
    experiment['initial_velocity'] = results.get('initial_velocity')
    experiment['initial_position'] = results.get('initial_position')
    experiment['error_margin'] = results.get('error_margin')
    experiment['graph_path'] = results.get('graph_path')
    
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(experiment, f, ensure_ascii=False, indent=2)

def get_results(team_name, experiment_id):
    experiment_dir = get_experiment_dir(team_name, experiment_id)
    results_file = os.path.join(experiment_dir, 'results.json')
    
    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return None

def delete_team(team_id):
    teams = load_teams()
    
    team_to_delete = None
    for team in teams:
        if team['id'] == team_id:
            team_to_delete = team
            break
    
    if not team_to_delete:
        return False
    
    team_dir = get_team_dir(team_to_delete['name'])
    if os.path.exists(team_dir):
        import shutil
        shutil.rmtree(team_dir)
    
    teams = [team for team in teams if team['id'] != team_id]
    save_teams(teams)
    
    return True

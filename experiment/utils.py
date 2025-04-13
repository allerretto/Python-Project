import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit
from django.conf import settings
from . import file_storage

def quadratic_function(t, a, v0, x0):
    return 0.5 * a * t**2 + v0 * t + x0

def analyze_data(times, positions, experiment_id, team_name):
    times = np.array(times)
    positions = np.array(positions)
    
    try:
        initial_guess = [9.8, 0, positions[0] if len(positions) > 0 else 0]
        
        params, covariance = curve_fit(quadratic_function, times, positions, p0=initial_guess)
        
        a, v0, x0 = params
        
        y_fit = quadratic_function(times, a, v0, x0)
        residuals = positions - y_fit
        error = np.sqrt(np.mean(residuals**2))
        
        plt.figure(figsize=(10, 6))
        
        plt.scatter(times, positions, color='blue', label='Экспериментальные данные')
        
        t_fit = np.linspace(min(times), max(times), 100)
        y_fit = quadratic_function(t_fit, a, v0, x0)
        plt.plot(t_fit, y_fit, 'r-', label=f'Аппроксимация: x(t) = {a/2:.2f}t² + {v0:.2f}t + {x0:.2f}')
        
        plt.xlabel('Время (с)')
        plt.ylabel('Положение (м)')
        plt.title(f'Анализ свободного падения - Эксперимент #{experiment_id}')
        plt.grid(True)
        plt.legend()
        
        experiment_dir = file_storage.get_experiment_dir(team_name, experiment_id)
        
        graph_filename = f"graph.png"
        graph_path = os.path.join(experiment_dir, graph_filename)
        plt.savefig(graph_path)
        plt.close()
        
        results = {
            'acceleration': float(a),
            'initial_velocity': float(v0),
            'initial_position': float(x0),
            'error_margin': float(error),
            'graph_path': graph_path,
            'equation': f"x(t) = {a/2:.4f}t² + {v0:.4f}t + {x0:.4f}",
            'r_squared': float(1 - (np.sum(residuals**2) / np.sum((positions - np.mean(positions))**2))),
            'data_points': len(times),
            'time_range': [float(min(times)), float(max(times))],
            'position_range': [float(min(positions)), float(max(positions))]
        }
        
        return results
    
    except Exception as e:
        return {
            'error': str(e),
            'acceleration': None,
            'initial_velocity': None,
            'initial_position': None,
            'error_margin': None,
            'graph_path': None
        }

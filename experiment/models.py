from django.utils import timezone
import os

def get_folder_path(team_name, date_str=None):
    if date_str is None:
        date_str = timezone.now().strftime("%Y-%m-%d")
    folder_name = f"{team_name}_{date_str}"
    return os.path.join('media', 'experiments', folder_name)

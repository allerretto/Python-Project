from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('', views.index, name='index'),
    path('team/create/', views.create_team_view, name='create_team'),
    path('team/<int:team_id>/experiments/', views.team_experiments_view, name='team_experiments'),
    path('team/<int:team_id>/experiment/create/', views.create_experiment_view, name='create_experiment'),
    path('experiment/<int:experiment_id>/edit/', views.edit_experiment_view, name='edit_experiment'),
    path('experiment/<int:experiment_id>/results/', views.experiment_results_view, name='experiment_results'),
    path('find-team/', views.find_team_view, name='find_team'),
    
    path('custom-admin/login/', views.admin_login_view, name='admin_login'),
    path('custom-admin/teams/', views.admin_teams_view, name='admin_teams'),
    path('custom-admin/team/<int:team_id>/delete/', views.admin_delete_team_view, name='admin_delete_team'),
    
    path('data/<path:path>', serve, {'document_root': settings.BASE_DIR / 'data'}, name='data_files'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.dashboard_view, name='dashboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Results
    path('results/', views.results_view, name='results_list'),
    path('results/<int:simulation_id>/', views.results_view, name='results'),
    
    # AI Experiments
    path('experiments/', views.ai_experiment_view, name='experiment_list'),
    path('experiments/<int:experiment_id>/', views.ai_experiment_view, name='ai_experiment'),
    
    # Simulation actions
    path('simulation/start/', views.start_simulation_view, name='start_simulation'),
    path('simulation/<int:simulation_id>/', views.simulation_detail_view, name='simulation_detail'),
    # Add this line for simulation list
    #path('simulations/', views.simulation_list_view, name='simulation_list'),
    
    # Scenario management
    path('scenarios/', views.scenario_list_view, name='scenario_list'),
    path('scenarios/create/', views.create_scenario_view, name = 'create_scenario'),
    path('scenarios/<int:scenario_id>/edit/', views.edit_scenario_view, name='edit_scenario'),
    
    # Comparison
    path('compare/', views.comparison_view, name='comparison'),
    path('compare/<int:comparison_id>/', views.comparison_detail_view, name='comparison_detail'),
    
    # Export
    path('export/csv/<int:simulation_id>/', views.export_csv_view, name='export_csv'),
    path('export/pdf/<int:simulation_id>/', views.export_pdf_view, name='export_pdf'),

    # API endpoints
    path('api/simulation/<int:simulation_id>/update/', views.api_update_simulation, name='api_update_simulation'),
    path('api/simulation/<int:simulation_id>/add-vehicle/', views.api_add_vehicle, name='api_add_vehicle'),
]

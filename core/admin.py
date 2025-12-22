from django.contrib import admin
from .models import (
    Scenario, Simulation, Vehicle, Metric, 
    Result, SimulationLog, Comparison
)

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario_type', 'is_active', 'created_at']
    list_filter = ['scenario_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ['name', 'scenario', 'algorithm', 'status', 'progress', 'created_at']
    list_filter = ['status', 'algorithm', 'scenario', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'started_at', 'completed_at']
    list_editable = ['status']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_id', 'simulation', 'vehicle_type', 'speed', 'timestamp']
    list_filter = ['vehicle_type', 'timestamp']
    search_fields = ['vehicle_id']
    readonly_fields = ['timestamp']

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['simulation', 'metric_type', 'value', 'unit', 'timestamp']
    list_filter = ['metric_type', 'timestamp']
    search_fields = ['simulation__name']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['simulation', 'avg_travel_time', 'improvement_travel_time', 'created_at']
    list_filter = ['created_at']
    search_fields = ['simulation__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SimulationLog)
class SimulationLogAdmin(admin.ModelAdmin):
    list_display = ['simulation', 'log_level', 'message_short', 'timestamp']
    list_filter = ['log_level', 'timestamp']
    search_fields = ['message', 'simulation__name']
    readonly_fields = ['timestamp']
    
    def message_short(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Message'

@admin.register(Comparison)
class ComparisonAdmin(admin.ModelAdmin):
    list_display = ['baseline_simulation', 'ai_simulation', 'created_at']
    list_filter = ['created_at']
    search_fields = ['baseline_simulation__name', 'ai_simulation__name']
    readonly_fields = ['created_at']
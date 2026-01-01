from django.db import models
from django.contrib.auth.models import User
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

class Scenario(models.Model):
    """Traffic simulation scenarios"""
    SCENARIO_TYPES = [
        ('nairobi_peak', 'Nairobi Peak Hour'),
        ('nakuru_central', 'Nakuru Central'),
        ('mombasa_coastal', 'Mombasa Coastal'),
        ('kisumu_lakeside', 'Kisumu Lakeside'),
    ]
    
    name = models.CharField(max_length=100)
    scenario_type = models.CharField(max_length=50, choices=SCENARIO_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    
    # To this:
    parameters = models.TextField(
        default = '{}',  # Empty JSON object as string
        blank = True,
        help_text = 'Enter valid JSON format'
        )

    def __str__(self):
        return f"{self.name} ({self.get_scenario_type_display()})"

class Simulation(models.Model):
    """Main simulation runs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    ALGORITHM_CHOICES = [
        ('baseline', 'Baseline (Current)'),
        ('rl_optimized', 'Reinforcement Learning'),
        ('ga_optimized', 'Genetic Algorithm'),
        ('hybrid', 'Hybrid AI'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)
    algorithm = models.CharField(max_length=50, choices=ALGORITHM_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Training parameters
    # To this:
    parameters = models.TextField(
        default = '{}',  # Empty JSON object as string
        blank = True,
        help_text = 'JSON parameters for the simulation'
)
    
    # Progress tracking
    progress = models.FloatField(default=0.0)  # 0-100%
    current_epoch = models.IntegerField(default=0)
    total_epochs = models.IntegerField(default=100)
    current_loss = models.FloatField(null=True, blank=True)
    current_accuracy = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if self.status == 'running' and not self.started_at:
            self.started_at = timezone.now()
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class Vehicle(models.Model):
    """Individual vehicle in simulation"""
    VEHICLE_TYPES = [
        ('car', 'Car'),
        ('bus', 'Bus'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
    ]
    
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_id = models.CharField(max_length=50)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    lat = models.FloatField()  # Latitude
    lng = models.FloatField()  # Longitude
    speed = models.FloatField(default=0.0)  # km/h
    heading = models.FloatField(default=0.0)  # degrees
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.vehicle_id} ({self.get_vehicle_type_display()})"

class Metric(models.Model):
    """Performance metrics for simulations"""
    METRIC_TYPES = [
        ('travel_time', 'Average Travel Time'),
        ('delay', 'Total Delay'),
        ('fuel', 'Fuel Consumption'),
        ('emissions', 'CO2 Emissions'),
        ('speed', 'Average Speed'),
        ('congestion', 'Congestion Level'),
    ]
    
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='metrics')
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    value = models.FloatField()
    unit = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # For comparison with baseline
    baseline_value = models.FloatField(null=True, blank=True)
    improvement_percentage = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['metric_type', '-timestamp']
    
    def __str__(self):
        return f"{self.get_metric_type_display()}: {self.value} {self.unit}"

class Result(models.Model):
    """Aggregated results for a simulation"""
    simulation = models.OneToOneField(Simulation, on_delete=models.CASCADE, related_name='result')
    
    # Key performance indicators
    avg_travel_time = models.FloatField(help_text="Minutes")
    baseline_avg_travel_time = models.FloatField()
    improvement_travel_time = models.FloatField(help_text="Percentage improvement")
    
    total_delay = models.FloatField(help_text="Hours")
    baseline_total_delay = models.FloatField()
    delay_reduction = models.FloatField(help_text="Percentage reduction")
    
    fuel_consumed = models.FloatField(help_text="Liters")
    baseline_fuel_consumed = models.FloatField()
    fuel_saving = models.FloatField(help_text="Percentage saving")
    
    co2_emissions = models.FloatField(help_text="kg CO2")
    baseline_co2_emissions = models.FloatField()
    emissions_reduction = models.FloatField(help_text="Percentage reduction")
    
    # AI-specific metrics
    training_loss = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    training_accuracy = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    validation_loss = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    validation_accuracy = models.JSONField(default=list, encoder=DjangoJSONEncoder)
    
    # Export data
    csv_data = models.TextField(blank=True, help_text="CSV formatted data")
    pdf_report_path = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Results for {self.simulation.name}"

class SimulationLog(models.Model):
    """Log entries for simulation runs"""
    LOG_LEVELS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('debug', 'Debug'),
    ]
    
    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='logs')
    log_level = models.CharField(max_length=20, choices=LOG_LEVELS)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"[{self.log_level}] {self.message[:50]}..."

class Comparison(models.Model):
    """Comparison between different simulation runs"""
    baseline_simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='baseline_comparisons')
    ai_simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='ai_comparisons')
    
    # Comparison metrics
    comparison_data = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    summary = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['baseline_simulation', 'ai_simulation']
    
    def __str__(self):
        return f"Comparison: {self.baseline_simulation.name} vs {self.ai_simulation.name}"
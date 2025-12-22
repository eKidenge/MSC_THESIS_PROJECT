from django import forms
from .models import Scenario, Simulation

class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ['name', 'scenario_type', 'description', 'parameters']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'parameters': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': '{"duration": 3600, "vehicle_count": 1000, "intersections": 20}'
            }),
        }

class SimulationForm(forms.ModelForm):
    class Meta:
        model = Simulation
        fields = ['name', 'scenario', 'algorithm', 'description', 'parameters']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'parameters': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': '{"epochs": 100, "learning_rate": 0.001, "batch_size": 32}'
            }),
        }
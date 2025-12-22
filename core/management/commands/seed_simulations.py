from django.core.management.base import BaseCommand
from core.models import Scenario, Simulation, Vehicle
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models  # Add this import
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the database with scenarios, simulations, and vehicles'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('🚗 Seeding database with traffic data...')
        
        # Clear existing data if flag provided
        if kwargs.get('clear'):
            Vehicle.objects.all().delete()
            Simulation.objects.all().delete()
            Scenario.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing data'))
        
        # Get or create system user
        user, created = User.objects.get_or_create(
            username='system_user',
            defaults={
                'email': 'system@egerton.ac.ke',
                'first_name': 'System',
                'last_name': 'User',
                'is_active': False,
                'is_staff': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created system user: {user.username}'))
        
        # ==============================================
        # 1. CREATE SCENARIOS
        # ==============================================
        
        scenarios = []
        scenario_names = [
            'Nairobi CBD Morning Rush',
            'Mombasa Ferry Traffic',
            'Kisumu Market Day',
            'Nakuru Highway',
            'Eldoret Industrial Zone'
        ]
        
        for i, name in enumerate(scenario_names):
            scenario, created = Scenario.objects.get_or_create(
                name=name,
                defaults={
                    'scenario_type': random.choice(['urban', 'highway', 'event', 'emergency']),
                    'description': f'Traffic simulation for {name}',
                    'created_by': user,
                    'is_active': True,
                    'parameters': {
                        'vehicle_count': random.randint(500, 2000),
                        'duration_minutes': random.choice([60, 90, 120, 180]),
                        'intersections': random.randint(10, 40),
                        'difficulty': random.choice(['easy', 'medium', 'hard']),
                        'weather': random.choice(['clear', 'rainy', 'foggy']),
                    }
                }
            )
            scenarios.append(scenario)
            if created:
                self.stdout.write(f'  Created scenario: {name}')
        
        # ==============================================
        # 2. CREATE SIMULATIONS
        # ==============================================
        
        simulations = []
        algorithms = ['rl_optimized', 'ga_optimized', 'hybrid', 'baseline']
        statuses = ['completed', 'running', 'pending', 'failed']
        
        for scenario in scenarios:
            # Create 2-3 simulations per scenario
            for i in range(random.randint(2, 3)):
                sim_name = f"{scenario.name.replace(' ', '_')}_{algorithms[i]}_{random.randint(100, 999)}"
                status = random.choice(statuses)
                
                simulation = Simulation.objects.create(
                    name=sim_name,
                    scenario=scenario,
                    algorithm=algorithms[i],
                    description=f'{algorithms[i].replace("_", " ").title()} test for {scenario.name}',
                    created_by=user,
                    status=status,
                    parameters={
                        'learning_rate': random.uniform(0.001, 0.01),
                        'epochs': 100,
                        'batch_size': random.choice([32, 64, 128]),
                        'vehicle_types': ['car', 'bus', 'truck', 'motorcycle']
                    },
                    total_epochs=100,
                    progress=100 if status == 'completed' else random.randint(0, 99),
                    current_epoch=100 if status == 'completed' else random.randint(0, 99),
                    current_loss=random.uniform(0.1, 0.5) if status != 'pending' else None,
                    current_accuracy=random.uniform(70, 95) if status == 'completed' else None,
                    started_at=timezone.now() - timedelta(hours=random.randint(1, 5)) if status in ['completed', 'running', 'failed'] else None,
                    completed_at=timezone.now() if status == 'completed' else None,
                )
                simulations.append(simulation)
                self.stdout.write(f'  Created simulation: {sim_name} ({status})')
        
        # ==============================================
        # 3. CREATE VEHICLES FOR EACH SIMULATION
        # ==============================================
        
        vehicle_types = ['car', 'bus', 'truck', 'motorcycle']
        nairobi_coords = (-1.2921, 36.8219)  # Nairobi coordinates
        vehicle_count = 0
        
        for simulation in simulations:
            if simulation.status != 'completed':
                continue  # Only add vehicles to completed simulations
            
            # Get number of vehicles from scenario parameters
            num_vehicles = random.randint(100, 500)
            
            for i in range(num_vehicles):
                # Generate realistic vehicle data
                vehicle_id = f"VH{simulation.id:03d}{i:04d}"
                vehicle_type = random.choice(vehicle_types)
                
                # Base speeds by vehicle type
                base_speeds = {
                    'car': random.uniform(20, 80),
                    'bus': random.uniform(15, 50),
                    'truck': random.uniform(10, 60),
                    'motorcycle': random.uniform(25, 90)
                }
                
                # Generate random coordinates around Nairobi
                lat = nairobi_coords[0] + random.uniform(-0.05, 0.05)
                lng = nairobi_coords[1] + random.uniform(-0.05, 0.05)
                
                Vehicle.objects.create(
                    simulation=simulation,
                    vehicle_id=vehicle_id,
                    vehicle_type=vehicle_type,
                    lat=lat,
                    lng=lng,
                    speed=base_speeds[vehicle_type],
                    heading=random.uniform(0, 360),
                    timestamp=timezone.now() - timedelta(minutes=random.randint(1, 60))
                )
                vehicle_count += 1
            
            self.stdout.write(f'  Added {num_vehicles} vehicles to {simulation.name}')
        
        # ==============================================
        # 4. SUMMARY
        # ==============================================
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('SEEDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        
        self.stdout.write(f'✅ Scenarios created: {len(scenarios)}')
        self.stdout.write(f'✅ Simulations created: {len(simulations)}')
        self.stdout.write(f'✅ Vehicles created: {vehicle_count}')
        
        # Breakdown by vehicle type
        vehicle_types_count = Vehicle.objects.values('vehicle_type').annotate(count=models.Count('id'))
        self.stdout.write('\nVehicle Type Breakdown:')
        for vt in vehicle_types_count:
            self.stdout.write(f'  • {vt["vehicle_type"].title()}: {vt["count"]}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('='*50))
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )
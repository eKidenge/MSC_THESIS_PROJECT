# core/management/commands/seed_results.py
from django.core.management.base import BaseCommand
from core.models import Scenario, Simulation, Result, Metric, Vehicle
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg, Sum, Count
import random
import json
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the database with realistic simulation results and metrics'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('📊 Seeding database with simulation results...')
        
        # Clear existing data if flag provided
        if kwargs.get('clear'):
            Metric.objects.all().delete()
            Result.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared all existing results and metrics'))
        
        # Get all completed simulations
        completed_simulations = Simulation.objects.filter(status='completed')
        
        if not completed_simulations.exists():
            self.stdout.write(self.style.ERROR('❌ No completed simulations found! Please run some simulations first.'))
            return
        
        results_created = 0
        metrics_created = 0
        
        # ==============================================
        # 1. CREATE RESULTS FOR EACH SIMULATION
        # ==============================================
        
        for simulation in completed_simulations:
            # Skip if result already exists
            if Result.objects.filter(simulation=simulation).exists():
                self.stdout.write(f'  ✓ Result already exists for: {simulation.name}')
                continue
            
            # Get or create baseline simulation for this scenario
            baseline_simulation = Simulation.objects.filter(
                scenario=simulation.scenario,
                algorithm='baseline',
                status='completed'
            ).first()
            
            # Generate realistic baseline values
            if baseline_simulation:
                # If we have a real baseline, use it
                try:
                    baseline_result = Result.objects.get(simulation=baseline_simulation)
                    baseline_travel_time = baseline_result.avg_travel_time
                    baseline_fuel = baseline_result.baseline_fuel_consumed
                    baseline_emissions = baseline_result.baseline_co2_emissions
                    baseline_delay = baseline_result.baseline_total_delay
                except Result.DoesNotExist:
                    # Generate realistic baseline values
                    baseline_travel_time = random.uniform(45, 75)  # minutes
                    baseline_fuel = random.uniform(8000, 12000)    # liters
                    baseline_emissions = random.uniform(18000, 25000)  # kg
                    baseline_delay = random.uniform(100, 200)      # hours
            else:
                # Generate realistic baseline values
                baseline_travel_time = random.uniform(45, 75)  # minutes
                baseline_fuel = random.uniform(8000, 12000)    # liters
                baseline_emissions = random.uniform(18000, 25000)  # kg
                baseline_delay = random.uniform(100, 200)      # hours
            
            # Generate AI-optimized results with improvements
            # Improvement depends on algorithm type
            improvement_factors = {
                'rl_optimized': random.uniform(0.65, 0.85),  # 15-35% improvement
                'ga_optimized': random.uniform(0.70, 0.90),  # 10-30% improvement
                'hybrid': random.uniform(0.60, 0.80),        # 20-40% improvement
                'baseline': 1.0,                            # 0% improvement (baseline)
                'traditional': random.uniform(0.90, 0.95),   # 5-10% improvement
            }
            
            factor = improvement_factors.get(simulation.algorithm, 0.8)
            
            # Calculate AI results with improvement
            ai_travel_time = baseline_travel_time * factor
            ai_fuel = baseline_fuel * factor
            ai_emissions = baseline_emissions * factor
            ai_delay = baseline_delay * factor
            
            # Calculate improvement percentages
            improvement_travel_time = ((baseline_travel_time - ai_travel_time) / baseline_travel_time) * 100
            fuel_saving = ((baseline_fuel - ai_fuel) / baseline_fuel) * 100
            emissions_reduction = ((baseline_emissions - ai_emissions) / baseline_emissions) * 100
            delay_reduction = ((baseline_delay - ai_delay) / baseline_delay) * 100
            
            # Create the Result object
            result = Result.objects.create(
                simulation=simulation,
                avg_travel_time=ai_travel_time,
                baseline_avg_travel_time=baseline_travel_time,
                improvement_travel_time=improvement_travel_time,
                total_delay=ai_delay,
                baseline_total_delay=baseline_delay,
                delay_reduction=delay_reduction,
                fuel_consumed=ai_fuel,
                baseline_fuel_consumed=baseline_fuel,
                fuel_saving=fuel_saving,
                co2_emissions=ai_emissions,
                baseline_co2_emissions=baseline_emissions,
                emissions_reduction=emissions_reduction,
            )
            results_created += 1
            
            self.stdout.write(f'  ✅ Created result for: {simulation.name}')
            self.stdout.write(f'     → Travel time: {ai_travel_time:.1f} min (Improvement: {improvement_travel_time:.1f}%)')
            self.stdout.write(f'     → Fuel saved: {fuel_saving:.1f}%')
            
            # ==============================================
            # 2. CREATE METRICS FOR EACH SIMULATION
            # ==============================================
            
            # Parse simulation parameters if it's a JSON string
            try:
                if isinstance(simulation.parameters, str):
                    params = json.loads(simulation.parameters)
                else:
                    params = simulation.parameters
            except:
                params = {}
            
            metric_types = [
                ('travel_time', 'min', ai_travel_time),
                ('delay', 'hours', ai_delay),
                ('fuel', 'liters', ai_fuel),
                ('emissions', 'kg', ai_emissions),
                ('speed', 'km/h', random.uniform(25, 45)),
                ('congestion', '%', random.uniform(30, 80)),
                ('vehicle_count', 'vehicles', params.get('vehicle_count', 1000)),
                ('intersections', 'nodes', params.get('intersections', 20)),
            ]
            
            for metric_type, unit, base_value in metric_types:
                # Create multiple metric records over time
                for i in range(10):  # Create 10 metric records per type
                    # Add some variation to the values
                    variation = base_value * random.uniform(0.8, 1.2)
                    
                    # Create timestamp over the simulation duration
                    # Get duration from parameters or use default
                    duration_minutes = params.get('duration_minutes', 60)
                    
                    if simulation.started_at:
                        timestamp = simulation.started_at + timedelta(
                            minutes=random.randint(0, duration_minutes)
                        )
                    else:
                        timestamp = timezone.now()
                    
                    Metric.objects.create(
                        simulation=simulation,
                        metric_type=metric_type,
                        value=variation,
                        unit=unit,
                        timestamp=timestamp,
                    )
                    metrics_created += 1
            
            self.stdout.write(f'     → Added metrics: {len(metric_types)} types, 10 records each')
        
        # ==============================================
        # 3. CREATE BASELINE SIMULATIONS IF MISSING
        # ==============================================
        
        # Check for scenarios without baseline simulations
        all_scenarios = Scenario.objects.all()
        user = User.objects.filter(username='system_user').first()
        
        for scenario in all_scenarios:
            if not Simulation.objects.filter(scenario=scenario, algorithm='baseline', status='completed').exists():
                # Parse scenario parameters
                try:
                    if isinstance(scenario.parameters, str):
                        scenario_params = json.loads(scenario.parameters)
                    else:
                        scenario_params = scenario.parameters
                except:
                    scenario_params = {}
                
                # Create a baseline simulation
                baseline_sim = Simulation.objects.create(
                    name=f"Baseline_{scenario.name.replace(' ', '_')}_{random.randint(100, 999)}",
                    scenario=scenario,
                    algorithm='baseline',
                    description=f'Baseline control simulation for {scenario.name}',
                    created_by=user,
                    status='completed',
                    parameters=scenario.parameters,
                    total_epochs=1,
                    progress=100,
                    current_epoch=1,
                    started_at=timezone.now() - timedelta(hours=2),
                    completed_at=timezone.now() - timedelta(hours=1),
                )
                
                # Create baseline result
                baseline_travel_time = random.uniform(45, 75)
                baseline_fuel = random.uniform(8000, 12000)
                baseline_emissions = random.uniform(18000, 25000)
                baseline_delay = random.uniform(100, 200)
                
                Result.objects.create(
                    simulation=baseline_sim,
                    avg_travel_time=baseline_travel_time,
                    baseline_avg_travel_time=baseline_travel_time,
                    improvement_travel_time=0,  # No improvement for baseline
                    total_delay=baseline_delay,
                    baseline_total_delay=baseline_delay,
                    delay_reduction=0,
                    fuel_consumed=baseline_fuel,
                    baseline_fuel_consumed=baseline_fuel,
                    fuel_saving=0,
                    co2_emissions=baseline_emissions,
                    baseline_co2_emissions=baseline_emissions,
                    emissions_reduction=0,
                )
                
                self.stdout.write(f'  🔧 Created missing baseline for: {scenario.name}')
        
        # ==============================================
        # 4. SUMMARY
        # ==============================================
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('RESULTS SEEDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS('='*50))
        
        # Statistics
        total_results = Result.objects.count()
        total_metrics = Metric.objects.count()
        total_simulations = Simulation.objects.filter(status='completed').count()
        
        self.stdout.write(f'📈 Total Results in database: {total_results}')
        self.stdout.write(f'📊 Total Metrics in database: {total_metrics}')
        self.stdout.write(f'🚗 Completed simulations: {total_simulations}')
        
        # Show improvement statistics
        if total_results > 0:
            avg_improvement = Result.objects.aggregate(avg=Avg('improvement_travel_time'))['avg']
            avg_fuel_saving = Result.objects.aggregate(avg=Avg('fuel_saving'))['avg']
            avg_emissions_reduction = Result.objects.aggregate(avg=Avg('emissions_reduction'))['avg']
            
            self.stdout.write('\n📊 Average Improvements:')
            self.stdout.write(f'  • Travel time: {avg_improvement:.1f}%')
            self.stdout.write(f'  • Fuel savings: {avg_fuel_saving:.1f}%')
            self.stdout.write(f'  • Emissions reduction: {avg_emissions_reduction:.1f}%')
        
        # Breakdown by algorithm
        self.stdout.write('\n🎯 Results by Algorithm:')
        algorithm_stats = Result.objects.values('simulation__algorithm').annotate(
            count=Count('id'),
            avg_improvement=Avg('improvement_travel_time')
        )
        
        for stat in algorithm_stats:
            algorithm_name = dict(Simulation.ALGORITHM_CHOICES).get(stat['simulation__algorithm'], stat['simulation__algorithm'])
            self.stdout.write(f'  • {algorithm_name}: {stat["count"]} results, {stat["avg_improvement"]:.1f}% avg improvement')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Created {results_created} new results'))
        self.stdout.write(self.style.SUCCESS(f'✅ Created {metrics_created} new metrics'))
        self.stdout.write(self.style.SUCCESS('='*50))
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing results and metrics before seeding'
        )
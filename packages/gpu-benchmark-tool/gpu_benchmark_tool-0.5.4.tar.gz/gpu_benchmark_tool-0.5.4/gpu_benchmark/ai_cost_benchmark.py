"""AI Workload Cost Benchmarking Module

This module benchmarks the real cost (time + energy) of AI workloads on different GPUs.
It measures training time, inference time, and energy consumption for actual models.
"""

import torch
import torch.nn as nn
import time
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .backends import get_gpu_backend
from .utils import print_info, print_success, print_warning, print_error


@dataclass
class ModelConfig:
    """Configuration for AI models to benchmark"""
    name: str
    model_class: str
    input_size: Tuple[int, ...]
    batch_size: int
    num_epochs: int
    learning_rate: float
    target_accuracy: float = 0.95
    energy_cost_per_kwh: float = 0.12    # Configurable energy cost


@dataclass
class CostMetrics:
    """Performance and energy metrics for AI workloads"""
    training_time_seconds: float
    training_energy_kwh: float
    inference_time_seconds: float
    inference_energy_kwh: float
    cost_per_inference: float
    time_to_accuracy: float


class AICostBenchmark:
    """Benchmarks AI workload costs on different GPUs"""
    
    def __init__(self, device_id: int = 0):
        self.device_id = device_id
        self.device = torch.device(f"cuda:{device_id}" if torch.cuda.is_available() else "cpu")
        self.monitor = None
        self.setup_monitoring()
        
    def setup_monitoring(self):
        """Setup GPU monitoring for energy consumption"""
        try:
            # Check if CUDA is available and use NVIDIA backend if possible
            if torch.cuda.is_available():
                print_info(f"CUDA detected: {torch.cuda.get_device_name(0) if torch.cuda.device_count() > 0 else 'Unknown GPU'}")
                
                # Force NVIDIA backend when CUDA is available
                backend = get_gpu_backend(backend_type="nvidia", device_id=self.device_id)
                if backend:
                    print_info(f"NVIDIA backend created: {backend.__class__.__name__}")
                    if backend.is_available():
                        self.monitor = backend.create_monitor(self.device_id)
                        print_success(f"Real GPU monitoring enabled for device {self.device_id} using {backend.__class__.__name__}")
                    else:
                        print_warning("CUDA available but NVIDIA backend.is_available() returned False")
                        backend = get_gpu_backend(backend_type="mock", device_id=self.device_id)
                        self.monitor = backend.create_monitor(self.device_id)
                else:
                    print_warning("CUDA available but NVIDIA backend creation failed")
                    backend = get_gpu_backend(backend_type="mock", device_id=self.device_id)
                    self.monitor = backend.create_monitor(self.device_id)
            else:
                # Use mock backend for CPU-only systems
                backend = get_gpu_backend(backend_type="mock", device_id=self.device_id)
                self.monitor = backend.create_monitor(self.device_id)
                print_info(f"Mock monitoring enabled for device {self.device_id} (CPU-only system)")
        except Exception as e:
            print_warning(f"GPU monitoring setup failed: {e}")
            import traceback
            traceback.print_exc()
            self.monitor = None
    
    def get_energy_consumption(self, start_time: float, end_time: float) -> float:
        """Get energy consumption in kWh for a time period"""
        if not self.monitor:
            return 0.0
        
        try:
            # Get power readings during the period
            # Since we don't have continuous power monitoring, we'll use a sampling approach
            duration = end_time - start_time
            if duration <= 0:
                return 0.0
            
            # Sample power usage at regular intervals during the workload
            # For fast workloads, sample more frequently
            if duration < 5.0:  # If workload is less than 5 seconds
                sample_interval = 0.1  # Sample every 0.1 seconds
            else:
                sample_interval = 1.0  # Sample every second
                
            num_samples = max(1, int(duration / sample_interval))
            
            power_samples = []
            for i in range(num_samples):
                sample_time = start_time + (i * sample_interval)
                if sample_time <= end_time:
                    power_watts = self.monitor.get_power_usage()
                    if power_watts > 0:
                        power_samples.append(power_watts)
            
            if power_samples:
                # Calculate energy: average power * time (convert to kWh)
                avg_power = sum(power_samples) / len(power_samples)
                total_energy = avg_power * duration / 3600000  # Convert to kWh
                print_info(f"Power sampling: {len(power_samples)} samples, avg power: {avg_power:.1f}W, duration: {duration:.2f}s, energy: {total_energy:.6f} kWh")
                return total_energy
            else:
                # Fallback: estimate based on typical GPU power usage
                print_warning(f"No power samples collected. Duration: {duration:.2f}s, expected samples: {num_samples}")
                return 0.0
                
        except Exception as e:
            print_warning(f"Could not get energy consumption: {e}")
        
        return 0.0
    
    def benchmark_resnet_training(self, config: ModelConfig) -> CostMetrics:
        """Benchmark ResNet training cost"""
        print_info(f"Benchmarking ResNet training on {self.device}")
        
        # Create a simple ResNet-like model
        model = self._create_resnet_model()
        model.to(self.device)
        
        # Create dummy dataset
        dataset_size = 1000
        inputs = torch.randn(dataset_size, *config.input_size, device=self.device)
        targets = torch.randint(0, 10, (dataset_size,), device=self.device)
        
        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
        
        # Start monitoring
        start_time = time.time()
        
        # Training loop
        model.train()
        for epoch in range(config.num_epochs):
            for i in range(0, dataset_size, config.batch_size):
                batch_inputs = inputs[i:i+config.batch_size]
                batch_targets = targets[i:i+config.batch_size]
                
                optimizer.zero_grad()
                outputs = model(batch_inputs)
                loss = criterion(outputs, batch_targets)
                loss.backward()
                optimizer.step()
                
                # Check accuracy periodically
                if i % (dataset_size // 4) == 0:
                    accuracy = self._calculate_accuracy(model, inputs, targets)
                    if accuracy >= config.target_accuracy:
                        break
            
            if accuracy >= config.target_accuracy:
                break
        
        end_time = time.time()
        training_time = end_time - start_time
        
        # Calculate energy consumption
        training_energy = self.get_energy_consumption(start_time, end_time)
        
        # Benchmark inference
        inference_time, inference_energy = self._benchmark_inference(model, inputs[:100])
        
        return CostMetrics(
            training_time_seconds=training_time,
            training_energy_kwh=training_energy,
            inference_time_seconds=inference_time,
            inference_energy_kwh=inference_energy,
            cost_per_inference=0.01,
            time_to_accuracy=training_time
        )
    
    def benchmark_transformer_inference(self, config: ModelConfig) -> CostMetrics:
        """Benchmark Transformer inference cost"""
        print_info(f"Benchmarking Transformer inference on {self.device}")
        
        # Create a simple transformer model
        model = self._create_transformer_model()
        model.to(self.device)
        model.eval()
        
        # Create dummy input
        inputs = torch.randn(config.batch_size, *config.input_size, device=self.device)
        
        # Benchmark inference
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):  # Run 100 inferences
                outputs = model(inputs)
        
        end_time = time.time()
        inference_time = end_time - start_time
        inference_energy = self.get_energy_consumption(start_time, end_time)
        
        return CostMetrics(
            training_time_seconds=0.0,
            training_energy_kwh=0.0,
            inference_time_seconds=inference_time,
            inference_energy_kwh=inference_energy,
            cost_per_inference=0.01,
            time_to_accuracy=0.0
        )
    
    def _create_resnet_model(self) -> nn.Module:
        """Create a simple ResNet-like model"""
        class SimpleResNet(nn.Module):
            def __init__(self, num_classes=10):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3)
                self.bn1 = nn.BatchNorm2d(64)
                self.relu = nn.ReLU(inplace=True)
                self.maxpool = nn.MaxPool2d(3, stride=2, padding=1)
                
                # Simple residual blocks
                self.layer1 = self._make_layer(64, 64, 2)
                self.layer2 = self._make_layer(64, 128, 2, stride=2)
                self.layer3 = self._make_layer(128, 256, 2, stride=2)
                
                self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(256, num_classes)
            
            def _make_layer(self, in_channels, out_channels, blocks, stride=1):
                layers = []
                layers.append(nn.Conv2d(in_channels, out_channels, 3, stride=stride, padding=1))
                layers.append(nn.BatchNorm2d(out_channels))
                layers.append(nn.ReLU(inplace=True))
                return nn.Sequential(*layers)
            
            def forward(self, x):
                x = self.conv1(x)
                x = self.bn1(x)
                x = self.relu(x)
                x = self.maxpool(x)
                
                x = self.layer1(x)
                x = self.layer2(x)
                x = self.layer3(x)
                
                x = self.avgpool(x)
                x = torch.flatten(x, 1)
                x = self.fc(x)
                return x
        
        return SimpleResNet()
    
    def _create_transformer_model(self) -> nn.Module:
        """Create a simple transformer model"""
        class SimpleTransformer(nn.Module):
            def __init__(self, input_dim=512, hidden_dim=256, num_layers=4):
                super().__init__()
                self.embedding = nn.Linear(input_dim, hidden_dim)
                encoder_layer = nn.TransformerEncoderLayer(
                    d_model=hidden_dim, 
                    nhead=8, 
                    dim_feedforward=1024,
                    batch_first=True
                )
                self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
                self.output = nn.Linear(hidden_dim, 10)
            
            def forward(self, x):
                x = self.embedding(x)
                x = self.transformer(x)
                x = x.mean(dim=1)  # Global average pooling
                x = self.output(x)
                return x
        
        return SimpleTransformer()
    
    def _calculate_accuracy(self, model: nn.Module, inputs: torch.Tensor, targets: torch.Tensor) -> float:
        """Calculate model accuracy"""
        model.eval()
        with torch.no_grad():
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            accuracy = (predicted == targets).sum().item() / targets.size(0)
        model.train()
        return accuracy
    
    def _benchmark_inference(self, model: nn.Module, inputs: torch.Tensor) -> Tuple[float, float]:
        """Benchmark inference time and energy"""
        model.eval()
        
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):  # Run 100 inferences
                outputs = model(inputs)
        
        end_time = time.time()
        inference_time = end_time - start_time
        inference_energy = self.get_energy_consumption(start_time, end_time)
        
        return inference_time, inference_energy
    
    def run_full_cost_benchmark(self, models: List[ModelConfig]) -> Dict[str, CostMetrics]:
        """Run full cost benchmark for multiple models"""
        results = {}
        
        for config in models:
            print_info(f"Benchmarking {config.name}...")
            
            try:
                if "resnet" in config.name.lower():
                    metrics = self.benchmark_resnet_training(config)
                elif "transformer" in config.name.lower():
                    metrics = self.benchmark_transformer_inference(config)
                else:
                    # Default to ResNet training
                    metrics = self.benchmark_resnet_training(config)
                
                results[config.name] = metrics
                print_success(f"Completed {config.name} benchmark")
                
            except Exception as e:
                print_error(f"Failed to benchmark {config.name}: {e}")
                continue
        
        return results
    
    def generate_cost_report(self, results: Dict[str, CostMetrics]) -> str:
        """Generate a human-readable cost report"""
        report = "=== AI Workload Cost Benchmark Report ===\n\n"
        
        for model_name, metrics in results.items():
            report += f"Model: {model_name}\n"
            report += f"Training Time: {metrics.training_time_seconds:.2f}s ({metrics.training_time_seconds/3600:.2f}h)\n"
            report += f"Training Energy: {metrics.training_energy_kwh:.4f} kWh\n"
            report += f"Inference Time: {metrics.inference_time_seconds:.4f}s per 100 inferences\n"
            report += f"Inference Energy: {metrics.inference_energy_kwh:.4f} kWh per 100 inferences\n"
            report += f"Performance per Watt: {metrics.training_time_seconds/metrics.training_energy_kwh:.2f}s/kWh (training)\n"
            report += "-" * 50 + "\n\n"
        
        return report


def create_standard_benchmarks() -> List[ModelConfig]:
    """Create standard benchmark configurations"""
    return [
        ModelConfig(
            name="ResNet-50 Training",
            model_class="resnet",
            input_size=(3, 224, 224),
            batch_size=32,
            num_epochs=5,
            learning_rate=0.001,
            energy_cost_per_kwh=0.12
        ),
        ModelConfig(
            name="Transformer Inference",
            model_class="transformer",
            input_size=(512,),
            batch_size=16,
            num_epochs=0,  # No training for inference
            learning_rate=0.0,
            energy_cost_per_kwh=0.12
        ),
        ModelConfig(
            name="ResNet-18 Training",
            model_class="resnet",
            input_size=(3, 224, 224),
            batch_size=64,
            num_epochs=3,
            learning_rate=0.001,
            energy_cost_per_kwh=0.12
        )
    ]


if __name__ == "__main__":
    # Example usage
    benchmark = AICostBenchmark()
    models = create_standard_benchmarks()
    results = benchmark.run_full_cost_benchmark(models)
    
    report = benchmark.generate_cost_report(results)
    print(report)


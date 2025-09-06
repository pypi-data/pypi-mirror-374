"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
⭐ GitHub Sponsors: https://github.com/sponsors/benedictchen

👨‍💻 Author: Benedict Chen
💰 Donations: Help support this work! Buy me a coffee ☕, beer 🍺, lamborghini 🏎️, or private island 🏝️
💖 Please consider recurring donations to fully support continued research

Your support enables cutting-edge AI research for everyone! 🚀

Comprehensive Hardware Utils Coverage Tests
==========================================

Complete test coverage for hardware detection, optimization, and management.
"""

import pytest
import torch
import torch.nn as nn
import psutil
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from meta_learning.hardware_utils import (
    HardwareConfig, HardwareDetector, MemoryManager, ModelOptimizer,
    HardwareProfiler, create_hardware_config, setup_optimal_hardware
)


class TestHardwareConfig:
    """Test HardwareConfig class."""
    
    def test_hardware_config_creation(self):
        """Test HardwareConfig creation with all parameters."""
        config = HardwareConfig(
            device="cuda",
            mixed_precision=True,
            compile_model=False,
            memory_fraction=0.8,
            batch_size_multiplier=2.0,
            log_hardware_info=True,
            enable_profiling=False
        )
        
        assert config.device == "cuda"
        assert config.mixed_precision == True
        assert config.compile_model == False
        assert config.memory_fraction == 0.8
        assert config.batch_size_multiplier == 2.0
        assert config.log_hardware_info == True
        assert config.enable_profiling == False
    
    def test_hardware_config_defaults(self):
        """Test HardwareConfig default values."""
        config = HardwareConfig()
        
        assert config.device == "auto"
        assert config.mixed_precision == True
        assert config.compile_model == True
        assert config.memory_fraction == 0.9
        assert config.batch_size_multiplier == 1.0
        assert config.log_hardware_info == False
        assert config.enable_profiling == False


class TestHardwareDetector:
    """Test HardwareDetector class."""
    
    def test_detect_optimal_device_cuda_available(self):
        """Test device detection when CUDA is available."""
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.device_count', return_value=2):
                device = HardwareDetector.detect_optimal_device()
                assert device.type == "cuda"
    
    def test_detect_optimal_device_mps_available(self):
        """Test device detection when MPS is available."""
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.backends.mps.is_available', return_value=True):
                device = HardwareDetector.detect_optimal_device()
                assert device.type == "mps"
    
    def test_detect_optimal_device_cpu_only(self):
        """Test device detection when only CPU is available."""
        with patch('torch.cuda.is_available', return_value=False):
            with patch('torch.backends.mps.is_available', return_value=False):
                device = HardwareDetector.detect_optimal_device()
                assert device.type == "cpu"
    
    def test_get_device_info_cpu(self):
        """Test getting CPU device info."""
        info = HardwareDetector.get_device_info(torch.device("cpu"))
        
        assert "device_type" in info
        assert info["device_type"] == "cpu"
        assert "cpu_count" in info
        assert "memory_total" in info
    
    def test_get_device_info_cuda(self):
        """Test getting CUDA device info."""
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.get_device_properties') as mock_props:
                mock_props.return_value = MagicMock(
                    name="Test GPU",
                    total_memory=8589934592,  # 8GB
                    multi_processor_count=80,
                    major=8,
                    minor=0
                )
                
                info = HardwareDetector.get_device_info(torch.device("cuda:0"))
                
                assert info["device_type"] == "cuda"
                assert "gpu_name" in info
                assert "memory_total" in info
    
    def test_get_device_info_mps(self):
        """Test getting MPS device info."""
        info = HardwareDetector.get_device_info(torch.device("mps"))
        
        assert info["device_type"] == "mps"
        assert "memory_total" in info
    
    def test_estimate_optimal_batch_size_cpu(self):
        """Test batch size estimation for CPU."""
        model = nn.Sequential(nn.Linear(10, 5))
        
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.available = 8 * 1024**3  # 8GB
            
            batch_size = HardwareDetector.estimate_optimal_batch_size(
                model, torch.device("cpu"), input_shape=(1, 10)
            )
            
            assert isinstance(batch_size, int)
            assert batch_size > 0
            assert batch_size <= 128
    
    def test_estimate_optimal_batch_size_cuda(self):
        """Test batch size estimation for CUDA."""
        model = nn.Sequential(nn.Linear(10, 5))
        device = torch.device("cuda:0")
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.synchronize'):
                with patch('torch.cuda.memory_allocated', return_value=1024*1024):  # 1MB
                    with patch('torch.cuda.get_device_properties') as mock_props:
                        mock_props.return_value.total_memory = 8 * 1024**3  # 8GB
                        
                        batch_size = HardwareDetector.estimate_optimal_batch_size(
                            model, device, input_shape=(1, 10)
                        )
                        
                        assert isinstance(batch_size, int)
                        assert batch_size > 0
    
    def test_estimate_optimal_batch_size_cuda_error(self):
        """Test batch size estimation CUDA error handling."""
        model = nn.Sequential(nn.Linear(10, 5))
        device = torch.device("cuda:0")
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch.object(model, 'forward', side_effect=RuntimeError("CUDA error")):
                
                batch_size = HardwareDetector.estimate_optimal_batch_size(
                    model, device, input_shape=(1, 10)
                )
                
                assert batch_size == 32  # Default fallback
    
    def test_get_hardware_info(self):
        """Test comprehensive hardware info gathering."""
        info = HardwareDetector.get_hardware_info()
        
        assert isinstance(info, dict)
        assert "system" in info
        assert "cpu" in info
        assert "memory" in info
        assert "python_version" in info
        assert "torch_version" in info


class TestMemoryManager:
    """Test MemoryManager class."""
    
    def test_memory_manager_creation(self):
        """Test MemoryManager creation."""
        config = HardwareConfig(memory_fraction=0.7)
        manager = MemoryManager(config)
        
        assert manager.config.memory_fraction == 0.7
    
    def test_optimize_memory_cpu(self):
        """Test memory optimization for CPU."""
        config = HardwareConfig(device="cpu")
        manager = MemoryManager(config)
        
        # Should not raise any errors
        manager.optimize_memory(torch.device("cpu"))
    
    def test_optimize_memory_cuda(self):
        """Test memory optimization for CUDA."""
        config = HardwareConfig(device="cuda", memory_fraction=0.8)
        manager = MemoryManager(config)
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.set_per_process_memory_fraction') as mock_set_fraction:
                with patch('torch.cuda.empty_cache') as mock_empty_cache:
                    
                    manager.optimize_memory(torch.device("cuda:0"))
                    
                    mock_set_fraction.assert_called_once_with(0.8, 0)
                    mock_empty_cache.assert_called_once()
    
    def test_get_memory_usage_cpu(self):
        """Test memory usage for CPU."""
        config = HardwareConfig()
        manager = MemoryManager(config)
        
        usage = manager.get_memory_usage(torch.device("cpu"))
        
        assert isinstance(usage, dict)
        assert "total" in usage
        assert "available" in usage
        assert "used" in usage
    
    def test_get_memory_usage_cuda(self):
        """Test memory usage for CUDA."""
        config = HardwareConfig()
        manager = MemoryManager(config)
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.mem_get_info', return_value=(4096, 8192)):
                
                usage = manager.get_memory_usage(torch.device("cuda:0"))
                
                assert usage["total"] == 8192
                assert usage["available"] == 4096
                assert usage["used"] == 4096


class TestModelOptimizer:
    """Test ModelOptimizer class."""
    
    def test_model_optimizer_creation(self):
        """Test ModelOptimizer creation."""
        config = HardwareConfig(device="cpu", compile_model=True)
        optimizer = ModelOptimizer(config)
        
        assert optimizer.config.compile_model == True
        assert optimizer.device.type == "cpu"
    
    def test_prepare_model_cpu(self):
        """Test model preparation for CPU."""
        config = HardwareConfig(device="cpu", mixed_precision=False, compile_model=False)
        optimizer = ModelOptimizer(config)
        
        model = nn.Sequential(nn.Linear(10, 5), nn.ReLU())
        prepared_model = optimizer.prepare_model(model)
        
        # Model should be moved to CPU
        assert next(prepared_model.parameters()).device.type == "cpu"
    
    def test_prepare_model_cuda(self):
        """Test model preparation for CUDA."""
        config = HardwareConfig(device="cuda:0", mixed_precision=True, compile_model=False)
        optimizer = ModelOptimizer(config)
        
        model = nn.Sequential(nn.Linear(10, 5), nn.ReLU())
        
        with patch('torch.cuda.is_available', return_value=True):
            prepared_model = optimizer.prepare_model(model)
            
            # Model should be moved to CUDA
            assert next(prepared_model.parameters()).device.type == "cuda"
    
    def test_prepare_model_with_compilation(self):
        """Test model preparation with compilation."""
        config = HardwareConfig(device="cpu", compile_model=True)
        optimizer = ModelOptimizer(config)
        
        model = nn.Sequential(nn.Linear(10, 5))
        
        with patch('torch.compile') as mock_compile:
            mock_compile.return_value = model
            
            prepared_model = optimizer.prepare_model(model)
            
            # torch.compile should have been called
            mock_compile.assert_called_once()
    
    def test_prepare_model_compilation_error(self):
        """Test model preparation handles compilation errors."""
        config = HardwareConfig(device="cpu", compile_model=True)
        optimizer = ModelOptimizer(config)
        
        model = nn.Sequential(nn.Linear(10, 5))
        
        with patch('torch.compile', side_effect=Exception("Compilation failed")):
            # Should not raise error, should fallback gracefully
            prepared_model = optimizer.prepare_model(model)
            assert prepared_model is not None
    
    def test_enable_mixed_precision(self):
        """Test mixed precision enabling."""
        config = HardwareConfig(mixed_precision=True)
        optimizer = ModelOptimizer(config)
        
        # Should create autocast context
        context = optimizer._enable_mixed_precision()
        assert context is not None
    
    def test_disable_mixed_precision(self):
        """Test mixed precision disabling."""
        config = HardwareConfig(mixed_precision=False)
        optimizer = ModelOptimizer(config)
        
        # Should return None for no mixed precision
        context = optimizer._enable_mixed_precision()
        assert context is None


class TestHardwareProfiler:
    """Test HardwareProfiler class."""
    
    def test_profiler_creation(self):
        """Test HardwareProfiler creation."""
        config = HardwareConfig(enable_profiling=True)
        profiler = HardwareProfiler(config)
        
        assert profiler.config.enable_profiling == True
        assert profiler.enabled == True
    
    def test_profiler_disabled(self):
        """Test profiler when disabled."""
        config = HardwareConfig(enable_profiling=False)
        profiler = HardwareProfiler(config)
        
        assert profiler.enabled == False
        
        # Operations should be no-ops
        profiler.start_profiling()
        profiler.stop_profiling()
        profile_data = profiler.get_profile_data()
        assert profile_data == {}
    
    def test_profiler_context_manager(self):
        """Test profiler as context manager."""
        config = HardwareConfig(enable_profiling=True)
        profiler = HardwareProfiler(config)
        
        with patch.object(profiler, 'start_profiling') as mock_start:
            with patch.object(profiler, 'stop_profiling') as mock_stop:
                
                with profiler:
                    pass
                
                mock_start.assert_called_once()
                mock_stop.assert_called_once()
    
    def test_profiler_benchmark_function(self):
        """Test function benchmarking."""
        config = HardwareConfig(enable_profiling=True)
        profiler = HardwareProfiler(config)
        
        def test_function():
            return torch.randn(100, 100).sum()
        
        if profiler.enabled:
            result = profiler.benchmark_function(test_function, num_runs=3)
            
            assert isinstance(result, dict)
            assert "mean_time" in result
            assert "std_time" in result
            assert "min_time" in result
            assert "max_time" in result
        else:
            result = profiler.benchmark_function(test_function)
            assert result == {}


class TestHardwareUtilityFunctions:
    """Test utility functions."""
    
    def test_create_hardware_config_auto(self):
        """Test automatic hardware config creation."""
        config = create_hardware_config()
        
        assert isinstance(config, HardwareConfig)
        assert config.device == "auto"
    
    def test_create_hardware_config_explicit(self):
        """Test explicit hardware config creation."""
        config = create_hardware_config(
            device="cuda:1",
            mixed_precision=False,
            compile_model=True,
            memory_fraction=0.7,
            log_hardware_info=True
        )
        
        assert config.device == "cuda:1"
        assert config.mixed_precision == False
        assert config.compile_model == True
        assert config.memory_fraction == 0.7
        assert config.log_hardware_info == True
    
    def test_setup_optimal_hardware_no_config(self):
        """Test hardware setup without config."""
        model = nn.Sequential(nn.Linear(10, 5))
        
        optimized_model, used_config = setup_optimal_hardware(model)
        
        assert isinstance(used_config, HardwareConfig)
        assert optimized_model is not None
    
    def test_setup_optimal_hardware_with_config(self):
        """Test hardware setup with explicit config."""
        model = nn.Sequential(nn.Linear(10, 5))
        config = HardwareConfig(device="cpu", mixed_precision=False)
        
        optimized_model, used_config = setup_optimal_hardware(model, config)
        
        assert used_config is config
        assert next(optimized_model.parameters()).device.type == "cpu"
    
    def test_setup_optimal_hardware_logging(self):
        """Test hardware setup with logging enabled."""
        model = nn.Sequential(nn.Linear(10, 5))
        config = HardwareConfig(log_hardware_info=True)
        
        with patch('meta_learning.hardware_utils.logger') as mock_logger:
            optimized_model, used_config = setup_optimal_hardware(model, config)
            
            # Should have logged hardware info
            assert mock_logger.info.called


class TestHardwareEdgeCases:
    """Test edge cases and error handling."""
    
    def test_device_detection_with_errors(self):
        """Test device detection handles errors gracefully."""
        with patch('torch.cuda.is_available', side_effect=RuntimeError("CUDA error")):
            with patch('torch.backends.mps.is_available', return_value=False):
                device = HardwareDetector.detect_optimal_device()
                assert device.type == "cpu"  # Should fallback to CPU
    
    def test_batch_size_estimation_edge_cases(self):
        """Test batch size estimation edge cases."""
        model = nn.Sequential(nn.Linear(1000, 1000))  # Large model
        
        # Test with very small available memory
        with patch('psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.available = 1024  # 1KB
            
            batch_size = HardwareDetector.estimate_optimal_batch_size(
                model, torch.device("cpu"), input_shape=(1, 1000)
            )
            
            assert batch_size >= 1  # Should have minimum of 1
    
    def test_memory_optimization_errors(self):
        """Test memory optimization error handling."""
        config = HardwareConfig(device="cuda")
        manager = MemoryManager(config)
        
        with patch('torch.cuda.is_available', return_value=True):
            with patch('torch.cuda.set_per_process_memory_fraction', 
                      side_effect=RuntimeError("Memory error")):
                
                # Should not raise error
                manager.optimize_memory(torch.device("cuda:0"))
    
    def test_model_compilation_availability(self):
        """Test model compilation availability check."""
        config = HardwareConfig(compile_model=True)
        optimizer = ModelOptimizer(config)
        
        model = nn.Sequential(nn.Linear(5, 3))
        
        # Test when torch.compile is not available
        with patch('torch.compile', side_effect=AttributeError("No compile")):
            prepared_model = optimizer.prepare_model(model)
            # Should still work, just without compilation
            assert prepared_model is not None
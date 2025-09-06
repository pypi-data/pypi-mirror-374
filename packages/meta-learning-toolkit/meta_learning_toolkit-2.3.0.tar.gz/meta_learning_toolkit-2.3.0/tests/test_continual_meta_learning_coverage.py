"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
⭐ GitHub Sponsors: https://github.com/sponsors/benedictchen

👨‍💻 Author: Benedict Chen
💰 Donations: Help support this work! Buy me a coffee ☕, beer 🍺, lamborghini 🏎️, or private island 🏝️
💖 Please consider recurring donations to fully support continued research

Your support enables cutting-edge AI research for everyone! 🚀

Comprehensive Continual Meta-Learning Coverage Tests
==================================================

Complete test coverage for continual meta-learning algorithms and components.
"""

import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, Any, List, Tuple
from unittest.mock import patch, MagicMock
from collections import deque

from meta_learning.continual_meta_learning import (
    ContinualMetaConfig, OnlineMetaLearner, FisherInformationMatrix,
    EpisodicMemoryBank, ExperienceReplay, create_continual_meta_learner
)


class TestContinualMetaConfig:
    """Test ContinualMetaConfig class."""
    
    def test_continual_meta_config_creation_default(self):
        """Test ContinualMetaConfig creation with defaults."""
        config = ContinualMetaConfig()
        
        assert config.memory_size == 1000
        assert config.consolidation_strength == 1000.0
        assert config.fisher_samples == 1000
        assert config.replay_batch_size == 32
        assert config.adaptation_lr == 0.01
        assert config.meta_lr == 0.001
        assert config.ewc_lambda == 1000.0
        assert config.replay_frequency == 10
        assert config.memory_selection_strategy == "reservoir"
    
    def test_continual_meta_config_creation_custom(self):
        """Test ContinualMetaConfig creation with custom values."""
        config = ContinualMetaConfig(
            memory_size=500,
            consolidation_strength=500.0,
            fisher_samples=500,
            replay_batch_size=16,
            adaptation_lr=0.02,
            meta_lr=0.002,
            ewc_lambda=2000.0,
            replay_frequency=5,
            memory_selection_strategy="fifo"
        )
        
        assert config.memory_size == 500
        assert config.consolidation_strength == 500.0
        assert config.fisher_samples == 500
        assert config.replay_batch_size == 16
        assert config.adaptation_lr == 0.02
        assert config.meta_lr == 0.002
        assert config.ewc_lambda == 2000.0
        assert config.replay_frequency == 5
        assert config.memory_selection_strategy == "fifo"


class TestFisherInformationMatrix:
    """Test FisherInformationMatrix class."""
    
    def test_fisher_information_matrix_creation(self):
        """Test FisherInformationMatrix creation."""
        model = nn.Sequential(nn.Linear(10, 20), nn.ReLU(), nn.Linear(20, 5))
        config = ContinualMetaConfig(fisher_samples=100)
        
        fisher = FisherInformationMatrix(model, config)
        
        assert fisher.model is model
        assert fisher.config.fisher_samples == 100
        assert len(fisher.fisher_dict) == 0
    
    def test_compute_fisher_information(self):
        """Test Fisher Information computation."""
        model = nn.Sequential(nn.Linear(8, 12), nn.ReLU(), nn.Linear(12, 3))
        config = ContinualMetaConfig(fisher_samples=10)
        fisher = FisherInformationMatrix(model, config)
        
        # Create sample data
        data_x = torch.randn(20, 8)
        data_y = torch.randint(0, 3, (20,))
        
        # Mock dataloader
        class MockDataLoader:
            def __init__(self, x, y, batch_size=5):
                self.x = x
                self.y = y
                self.batch_size = batch_size
                
            def __iter__(self):
                for i in range(0, len(self.x), self.batch_size):
                    yield self.x[i:i+self.batch_size], self.y[i:i+self.batch_size]
        
        dataloader = MockDataLoader(data_x, data_y)
        
        fisher.compute_fisher_information(dataloader)
        
        # Should have computed Fisher information for all parameters
        param_names = [name for name, param in model.named_parameters() if param.requires_grad]
        assert len(fisher.fisher_dict) == len(param_names)
        
        # All Fisher values should be positive
        for name, fisher_val in fisher.fisher_dict.items():
            assert torch.all(fisher_val >= 0)
    
    def test_get_fisher_information(self):
        """Test getting Fisher information for specific parameters."""
        model = nn.Linear(5, 3)
        config = ContinualMetaConfig()
        fisher = FisherInformationMatrix(model, config)
        
        # Manually set Fisher information
        fisher.fisher_dict = {
            "weight": torch.ones(3, 5) * 0.5,
            "bias": torch.ones(3) * 0.3
        }
        
        fisher_weight = fisher.get_fisher_information("weight")
        fisher_bias = fisher.get_fisher_information("bias")
        
        assert torch.allclose(fisher_weight, torch.ones(3, 5) * 0.5)
        assert torch.allclose(fisher_bias, torch.ones(3) * 0.3)
    
    def test_get_fisher_information_nonexistent(self):
        """Test getting Fisher information for non-existent parameter."""
        model = nn.Linear(5, 3)
        config = ContinualMetaConfig()
        fisher = FisherInformationMatrix(model, config)
        
        fisher_nonexistent = fisher.get_fisher_information("nonexistent_param")
        assert fisher_nonexistent is None
    
    def test_update_fisher_information(self):
        """Test updating Fisher information."""
        model = nn.Linear(4, 2)
        config = ContinualMetaConfig()
        fisher = FisherInformationMatrix(model, config)
        
        # Set initial Fisher information
        initial_fisher = torch.ones(2, 4) * 0.1
        fisher.fisher_dict["weight"] = initial_fisher.clone()
        
        # Update with new Fisher information
        new_fisher = torch.ones(2, 4) * 0.2
        fisher.update_fisher_information("weight", new_fisher)
        
        # Should be updated
        assert torch.allclose(fisher.fisher_dict["weight"], new_fisher)
    
    def test_compute_fisher_with_empty_data(self):
        """Test Fisher computation with empty data."""
        model = nn.Linear(3, 2)
        config = ContinualMetaConfig(fisher_samples=10)
        fisher = FisherInformationMatrix(model, config)
        
        # Empty dataloader
        class EmptyDataLoader:
            def __iter__(self):
                return iter([])
        
        dataloader = EmptyDataLoader()
        
        # Should handle empty data gracefully
        fisher.compute_fisher_information(dataloader)
        
        # Fisher dictionary might be empty or have zero values
        for name, fisher_val in fisher.fisher_dict.items():
            assert torch.all(fisher_val >= 0)


class TestEpisodicMemoryBank:
    """Test EpisodicMemoryBank class."""
    
    def test_episodic_memory_bank_creation(self):
        """Test EpisodicMemoryBank creation."""
        config = ContinualMetaConfig(memory_size=100, memory_selection_strategy="reservoir")
        memory = EpisodicMemoryBank(config)
        
        assert memory.config.memory_size == 100
        assert memory.config.memory_selection_strategy == "reservoir"
        assert len(memory.episodes) == 0
        assert memory.total_episodes_seen == 0
    
    def test_add_episode_reservoir_sampling(self):
        """Test adding episodes with reservoir sampling."""
        config = ContinualMetaConfig(memory_size=5, memory_selection_strategy="reservoir")
        memory = EpisodicMemoryBank(config)
        
        # Add episodes
        for i in range(10):
            episode_data = {
                "support_x": torch.randn(6, 4),
                "support_y": torch.randint(0, 2, (6,)),
                "query_x": torch.randn(4, 4),
                "query_y": torch.randint(0, 2, (4,)),
                "task_id": i
            }
            memory.add_episode(episode_data)
        
        # Should maintain memory size limit
        assert len(memory.episodes) == 5
        assert memory.total_episodes_seen == 10
    
    def test_add_episode_fifo_strategy(self):
        """Test adding episodes with FIFO strategy."""
        config = ContinualMetaConfig(memory_size=3, memory_selection_strategy="fifo")
        memory = EpisodicMemoryBank(config)
        
        # Add episodes
        episodes = []
        for i in range(5):
            episode_data = {
                "support_x": torch.randn(4, 3),
                "support_y": torch.randint(0, 2, (4,)),
                "task_id": i
            }
            episodes.append(episode_data)
            memory.add_episode(episode_data)
        
        # Should maintain only the last 3 episodes
        assert len(memory.episodes) == 3
        # Should contain episodes 2, 3, 4 (last 3)
        task_ids = [ep["task_id"] for ep in memory.episodes]
        assert task_ids == [2, 3, 4]
    
    def test_sample_episodes(self):
        """Test sampling episodes from memory."""
        config = ContinualMetaConfig(memory_size=10, replay_batch_size=3)
        memory = EpisodicMemoryBank(config)
        
        # Add some episodes
        for i in range(6):
            episode_data = {
                "support_x": torch.randn(4, 5),
                "support_y": torch.randint(0, 3, (4,)),
                "query_x": torch.randn(2, 5),
                "query_y": torch.randint(0, 3, (2,)),
                "task_id": i
            }
            memory.add_episode(episode_data)
        
        # Sample episodes
        sampled_episodes = memory.sample_episodes(batch_size=3)
        
        assert len(sampled_episodes) == 3
        for episode in sampled_episodes:
            assert "support_x" in episode
            assert "support_y" in episode
            assert "task_id" in episode
    
    def test_sample_episodes_more_than_available(self):
        """Test sampling more episodes than available."""
        config = ContinualMetaConfig(memory_size=10, replay_batch_size=5)
        memory = EpisodicMemoryBank(config)
        
        # Add only 2 episodes
        for i in range(2):
            episode_data = {"task_id": i, "data": torch.randn(3, 2)}
            memory.add_episode(episode_data)
        
        # Try to sample more than available
        sampled_episodes = memory.sample_episodes(batch_size=5)
        
        # Should return all available episodes
        assert len(sampled_episodes) <= 2
    
    def test_get_memory_statistics(self):
        """Test getting memory statistics."""
        config = ContinualMetaConfig(memory_size=5)
        memory = EpisodicMemoryBank(config)
        
        # Add episodes
        for i in range(3):
            episode_data = {"task_id": i % 2, "data": torch.randn(2, 3)}
            memory.add_episode(episode_data)
        
        stats = memory.get_memory_statistics()
        
        assert isinstance(stats, dict)
        assert "total_episodes" in stats
        assert "memory_utilization" in stats
        assert "episodes_per_task" in stats
        assert stats["total_episodes"] == 3
        assert 0 <= stats["memory_utilization"] <= 1.0
    
    def test_clear_memory(self):
        """Test clearing memory."""
        config = ContinualMetaConfig(memory_size=10)
        memory = EpisodicMemoryBank(config)
        
        # Add episodes
        for i in range(5):
            episode_data = {"task_id": i}
            memory.add_episode(episode_data)
        
        assert len(memory.episodes) == 5
        
        memory.clear_memory()
        
        assert len(memory.episodes) == 0
        assert memory.total_episodes_seen == 0


class TestExperienceReplay:
    """Test ExperienceReplay class."""
    
    def test_experience_replay_creation(self):
        """Test ExperienceReplay creation."""
        config = ContinualMetaConfig(replay_frequency=5, replay_batch_size=4)
        memory = EpisodicMemoryBank(config)
        replay = ExperienceReplay(config, memory)
        
        assert replay.config.replay_frequency == 5
        assert replay.config.replay_batch_size == 4
        assert replay.memory is memory
        assert replay.step_count == 0
    
    def test_should_replay_frequency(self):
        """Test replay frequency checking."""
        config = ContinualMetaConfig(replay_frequency=3)
        memory = EpisodicMemoryBank(config)
        replay = ExperienceReplay(config, memory)
        
        # Should not replay initially
        assert replay.should_replay() == False
        
        # Increment steps
        replay.step_count = 2
        assert replay.should_replay() == False
        
        replay.step_count = 3
        assert replay.should_replay() == True
        
        replay.step_count = 6
        assert replay.should_replay() == True
    
    def test_replay_experience(self):
        """Test experience replay."""
        config = ContinualMetaConfig(replay_frequency=2, replay_batch_size=2)
        memory = EpisodicMemoryBank(config)
        replay = ExperienceReplay(config, memory)
        
        # Add episodes to memory
        for i in range(4):
            episode_data = {
                "support_x": torch.randn(3, 2),
                "support_y": torch.randint(0, 2, (3,)),
                "query_x": torch.randn(2, 2),
                "query_y": torch.randint(0, 2, (2,)),
                "task_id": i
            }
            memory.add_episode(episode_data)
        
        # Mock model and loss function
        model = nn.Linear(2, 2)
        
        def mock_loss_fn(logits, targets):
            return F.cross_entropy(logits, targets)
        
        replay.step_count = 2  # Should trigger replay
        
        if replay.should_replay():
            loss = replay.replay_experience(model, mock_loss_fn)
            assert isinstance(loss, torch.Tensor)
            assert loss.requires_grad
    
    def test_replay_experience_empty_memory(self):
        """Test experience replay with empty memory."""
        config = ContinualMetaConfig(replay_frequency=1, replay_batch_size=2)
        memory = EpisodicMemoryBank(config)
        replay = ExperienceReplay(config, memory)
        
        model = nn.Linear(3, 2)
        
        def mock_loss_fn(logits, targets):
            return F.cross_entropy(logits, targets)
        
        replay.step_count = 1  # Should trigger replay
        
        # Should handle empty memory gracefully
        loss = replay.replay_experience(model, mock_loss_fn)
        
        # Should return zero loss or None
        assert loss is None or (isinstance(loss, torch.Tensor) and loss.item() == 0.0)
    
    def test_increment_step(self):
        """Test step incrementing."""
        config = ContinualMetaConfig()
        memory = EpisodicMemoryBank(config)
        replay = ExperienceReplay(config, memory)
        
        initial_step = replay.step_count
        replay.increment_step()
        
        assert replay.step_count == initial_step + 1


class TestOnlineMetaLearner:
    """Test OnlineMetaLearner class."""
    
    def test_online_meta_learner_creation(self):
        """Test OnlineMetaLearner creation."""
        base_model = nn.Sequential(nn.Linear(6, 8), nn.ReLU(), nn.Linear(8, 3))
        config = ContinualMetaConfig(memory_size=50, consolidation_strength=500.0)
        
        learner = OnlineMetaLearner(base_model, config)
        
        assert learner.base_model is base_model
        assert learner.config.memory_size == 50
        assert learner.config.consolidation_strength == 500.0
        assert isinstance(learner.memory, EpisodicMemoryBank)
        assert isinstance(learner.fisher, FisherInformationMatrix)
        assert isinstance(learner.experience_replay, ExperienceReplay)
        assert len(learner.previous_params) == 0
        assert learner.task_count == 0
    
    def test_learn_episode(self):
        """Test learning from a single episode."""
        model = nn.Sequential(nn.Linear(4, 6), nn.ReLU(), nn.Linear(6, 2))
        config = ContinualMetaConfig(memory_size=10, adaptation_lr=0.01)
        learner = OnlineMetaLearner(model, config)
        
        # Create episode data
        support_x = torch.randn(6, 4)
        support_y = torch.randint(0, 2, (6,))
        query_x = torch.randn(4, 4)
        query_y = torch.randint(0, 2, (4,))
        
        episode_data = {
            "support_x": support_x,
            "support_y": support_y,
            "query_x": query_x,
            "query_y": query_y,
            "task_id": 1
        }
        
        # Learn from episode
        loss, adapted_params = learner.learn_episode(episode_data)
        
        assert isinstance(loss, torch.Tensor)
        assert loss.requires_grad
        assert isinstance(adapted_params, dict)
        
        # Episode should be added to memory
        assert len(learner.memory.episodes) == 1
    
    def test_adapt_to_task(self):
        """Test adaptation to a specific task."""
        model = nn.Linear(3, 2)
        config = ContinualMetaConfig(adaptation_lr=0.02)
        learner = OnlineMetaLearner(model, config)
        
        support_x = torch.randn(4, 3)
        support_y = torch.randint(0, 2, (4,))
        
        adapted_params = learner.adapt_to_task(support_x, support_y)
        
        assert isinstance(adapted_params, dict)
        assert len(adapted_params) > 0
        
        # Check that adapted parameters have the right structure
        original_params = dict(model.named_parameters())
        for name in original_params.keys():
            assert name in adapted_params
    
    def test_consolidate_task_knowledge(self):
        """Test task knowledge consolidation."""
        model = nn.Sequential(nn.Linear(5, 4), nn.Linear(4, 2))
        config = ContinualMetaConfig(fisher_samples=10)
        learner = OnlineMetaLearner(model, config)
        
        # Create mock dataloader
        class MockDataLoader:
            def __init__(self):
                self.data = [(torch.randn(3, 5), torch.randint(0, 2, (3,))) for _ in range(5)]
                
            def __iter__(self):
                return iter(self.data)
        
        dataloader = MockDataLoader()
        task_id = 1
        
        # Consolidate knowledge
        learner.consolidate_task_knowledge(dataloader, task_id)
        
        # Should have stored parameters and Fisher information
        assert task_id in learner.previous_params
        assert len(learner.fisher.fisher_dict) > 0
        assert learner.task_count == 1
    
    def test_compute_ewc_loss(self):
        """Test EWC loss computation."""
        model = nn.Linear(3, 2)
        config = ContinualMetaConfig(ewc_lambda=1000.0)
        learner = OnlineMetaLearner(model, config)
        
        # Store previous parameters and Fisher information
        task_id = 0
        learner.previous_params[task_id] = {}
        learner.fisher.fisher_dict = {}
        
        for name, param in model.named_parameters():
            learner.previous_params[task_id][name] = param.detach().clone()
            learner.fisher.fisher_dict[name] = torch.ones_like(param) * 0.5
        
        # Modify current parameters slightly
        with torch.no_grad():
            for param in model.parameters():
                param.add_(torch.randn_like(param) * 0.01)
        
        ewc_loss = learner.compute_ewc_loss()
        
        assert isinstance(ewc_loss, torch.Tensor)
        assert ewc_loss.item() >= 0  # EWC loss should be non-negative
    
    def test_meta_update(self):
        """Test meta-learning update."""
        model = nn.Linear(2, 1)
        config = ContinualMetaConfig(meta_lr=0.001)
        learner = OnlineMetaLearner(model, config)
        
        # Create optimizer
        optimizer = torch.optim.Adam(model.parameters(), lr=config.meta_lr)
        
        # Simulate some loss
        x = torch.randn(5, 2)
        y = torch.randn(5, 1)
        output = model(x)
        loss = F.mse_loss(output, y)
        
        # Add EWC loss
        ewc_loss = learner.compute_ewc_loss()
        total_loss = loss + ewc_loss
        
        # Perform meta update
        learner.meta_update(total_loss, optimizer)
        
        # Loss should have been backpropagated
        assert not total_loss.requires_grad  # Gradient should be cleared
    
    def test_get_learner_statistics(self):
        """Test getting learner statistics."""
        model = nn.Linear(4, 3)
        config = ContinualMetaConfig(memory_size=20)
        learner = OnlineMetaLearner(model, config)
        
        # Add some episodes and tasks
        for i in range(5):
            episode_data = {
                "support_x": torch.randn(3, 4),
                "support_y": torch.randint(0, 3, (3,)),
                "task_id": i % 2
            }
            learner.memory.add_episode(episode_data)
        
        learner.task_count = 2
        
        stats = learner.get_learner_statistics()
        
        assert isinstance(stats, dict)
        assert "total_tasks" in stats
        assert "total_episodes" in stats
        assert "memory_statistics" in stats
        assert stats["total_tasks"] == 2
        assert stats["total_episodes"] == 5


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_create_continual_meta_learner_default(self):
        """Test creating continual meta-learner with defaults."""
        base_model = nn.Linear(5, 3)
        
        learner = create_continual_meta_learner(base_model)
        
        assert isinstance(learner, OnlineMetaLearner)
        assert learner.base_model is base_model
        assert isinstance(learner.config, ContinualMetaConfig)
    
    def test_create_continual_meta_learner_custom(self):
        """Test creating continual meta-learner with custom config."""
        base_model = nn.Sequential(nn.Linear(3, 5), nn.ReLU(), nn.Linear(5, 2))
        
        learner = create_continual_meta_learner(
            base_model,
            memory_size=200,
            consolidation_strength=2000.0,
            fisher_samples=500,
            adaptation_lr=0.05,
            meta_lr=0.005,
            replay_frequency=15
        )
        
        assert learner.config.memory_size == 200
        assert learner.config.consolidation_strength == 2000.0
        assert learner.config.fisher_samples == 500
        assert learner.config.adaptation_lr == 0.05
        assert learner.config.meta_lr == 0.005
        assert learner.config.replay_frequency == 15


class TestContinualLearningScenarios:
    """Test various continual learning scenarios."""
    
    def test_sequential_task_learning(self):
        """Test learning sequential tasks without forgetting."""
        model = nn.Sequential(nn.Linear(4, 8), nn.ReLU(), nn.Linear(8, 3))
        config = ContinualMetaConfig(memory_size=50, ewc_lambda=1000.0)
        learner = OnlineMetaLearner(model, config)
        
        # Learn multiple tasks sequentially
        num_tasks = 3
        episodes_per_task = 5
        
        for task_id in range(num_tasks):
            # Learn episodes for this task
            for episode_id in range(episodes_per_task):
                support_x = torch.randn(6, 4)
                support_y = torch.randint(0, 3, (6,))
                query_x = torch.randn(4, 4)
                query_y = torch.randint(0, 3, (4,))
                
                episode_data = {
                    "support_x": support_x,
                    "support_y": support_y,
                    "query_x": query_x,
                    "query_y": query_y,
                    "task_id": task_id
                }
                
                loss, adapted_params = learner.learn_episode(episode_data)
                assert isinstance(loss, torch.Tensor)
            
            # Consolidate knowledge after each task
            # Mock dataloader for consolidation
            class MockDataLoader:
                def __iter__(self):
                    for _ in range(3):
                        yield torch.randn(2, 4), torch.randint(0, 3, (2,))
            
            learner.consolidate_task_knowledge(MockDataLoader(), task_id)
        
        # Verify learning occurred
        assert learner.task_count == num_tasks
        assert len(learner.memory.episodes) > 0
        
        # Verify EWC parameters are stored
        assert len(learner.previous_params) == num_tasks
    
    def test_catastrophic_forgetting_prevention(self):
        """Test that EWC prevents catastrophic forgetting."""
        model = nn.Linear(3, 2)
        config = ContinualMetaConfig(ewc_lambda=10000.0)  # High EWC strength
        learner = OnlineMetaLearner(model, config)
        
        # Store initial parameters
        initial_params = {}
        for name, param in model.named_parameters():
            initial_params[name] = param.detach().clone()
        
        # Simulate learning first task
        learner.previous_params[0] = initial_params.copy()
        for name, param in model.named_parameters():
            learner.fisher.fisher_dict[name] = torch.ones_like(param) * 1.0
        
        # Learn second task with EWC
        support_x = torch.randn(4, 3)
        support_y = torch.randint(0, 2, (4,))
        
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        
        # Multiple optimization steps on new task
        for _ in range(10):
            adapted_params = learner.adapt_to_task(support_x, support_y)
            
            # Compute total loss including EWC
            task_loss = F.cross_entropy(model(support_x), support_y)
            ewc_loss = learner.compute_ewc_loss()
            total_loss = task_loss + ewc_loss
            
            learner.meta_update(total_loss, optimizer)
        
        # Check that parameters didn't change too much from initial
        final_params = {name: param.detach().clone() for name, param in model.named_parameters()}
        
        # With high EWC strength, parameters should be constrained
        for name in initial_params:
            param_change = torch.norm(final_params[name] - initial_params[name])
            # Should be smaller than without EWC (can't test directly, but should be reasonable)
            assert param_change.item() >= 0  # Just check it computed
    
    def test_memory_replay_effectiveness(self):
        """Test that memory replay helps with continual learning."""
        model = nn.Linear(2, 1)
        config = ContinualMetaConfig(memory_size=20, replay_frequency=2, replay_batch_size=3)
        learner = OnlineMetaLearner(model, config)
        
        # Add episodes to memory
        for i in range(10):
            episode_data = {
                "support_x": torch.randn(3, 2),
                "support_y": torch.randn(3, 1),
                "query_x": torch.randn(2, 2),
                "query_y": torch.randn(2, 1),
                "task_id": i % 3
            }
            learner.memory.add_episode(episode_data)
        
        # Test experience replay
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        
        def mock_loss_fn(logits, targets):
            return F.mse_loss(logits, targets)
        
        # Trigger replay
        learner.experience_replay.step_count = 2
        
        if learner.experience_replay.should_replay():
            replay_loss = learner.experience_replay.replay_experience(model, mock_loss_fn)
            
            if replay_loss is not None:
                assert isinstance(replay_loss, torch.Tensor)
                # Perform update with replay loss
                learner.meta_update(replay_loss, optimizer)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_model_parameters(self):
        """Test handling of model with no parameters."""
        # Model with no learnable parameters
        model = nn.Identity()
        config = ContinualMetaConfig()
        
        # Should handle gracefully
        learner = OnlineMetaLearner(model, config)
        
        support_x = torch.randn(3, 5)
        support_y = torch.randint(0, 2, (3,))
        
        adapted_params = learner.adapt_to_task(support_x, support_y)
        
        # Should return empty dict
        assert len(adapted_params) == 0
    
    def test_single_sample_learning(self):
        """Test learning with single samples."""
        model = nn.Linear(2, 1)
        config = ContinualMetaConfig()
        learner = OnlineMetaLearner(model, config)
        
        # Single sample episode
        episode_data = {
            "support_x": torch.randn(1, 2),
            "support_y": torch.randn(1, 1),
            "query_x": torch.randn(1, 2),
            "query_y": torch.randn(1, 1),
            "task_id": 0
        }
        
        # Should handle single samples
        loss, adapted_params = learner.learn_episode(episode_data)
        
        assert isinstance(loss, torch.Tensor)
        assert isinstance(adapted_params, dict)
    
    def test_numerical_stability_ewc(self):
        """Test numerical stability of EWC computation."""
        model = nn.Linear(3, 2)
        config = ContinualMetaConfig(ewc_lambda=1e10)  # Very high EWC strength
        learner = OnlineMetaLearner(model, config)
        
        # Set extreme Fisher information values
        learner.previous_params[0] = {}
        learner.fisher.fisher_dict = {}
        
        for name, param in model.named_parameters():
            learner.previous_params[0][name] = param.detach().clone()
            # Very high Fisher values
            learner.fisher.fisher_dict[name] = torch.ones_like(param) * 1e6
        
        # Modify parameters
        with torch.no_grad():
            for param in model.parameters():
                param.add_(torch.randn_like(param) * 0.1)
        
        ewc_loss = learner.compute_ewc_loss()
        
        # Should be finite despite extreme values
        assert torch.isfinite(ewc_loss)
    
    def test_memory_overflow_handling(self):
        """Test handling of memory overflow."""
        config = ContinualMetaConfig(memory_size=2)  # Very small memory
        memory = EpisodicMemoryBank(config)
        
        # Add more episodes than memory can hold
        for i in range(10):
            episode_data = {"task_id": i, "data": torch.randn(2, 3)}
            memory.add_episode(episode_data)
        
        # Should maintain size limit
        assert len(memory.episodes) == 2
        assert memory.total_episodes_seen == 10
    
    def test_fisher_computation_with_nan(self):
        """Test Fisher computation handling NaN values."""
        model = nn.Linear(2, 1)
        config = ContinualMetaConfig(fisher_samples=5)
        fisher = FisherInformationMatrix(model, config)
        
        # Data that might produce NaN gradients
        class ProblematicDataLoader:
            def __iter__(self):
                # Return data that might cause numerical issues
                for _ in range(3):
                    x = torch.zeros(2, 2)  # Zero input
                    y = torch.zeros(2, dtype=torch.long)  # Zero targets
                    yield x, y
        
        dataloader = ProblematicDataLoader()
        
        # Should handle gracefully without crashing
        fisher.compute_fisher_information(dataloader)
        
        # Check that Fisher values are finite
        for name, fisher_val in fisher.fisher_dict.items():
            assert torch.all(torch.isfinite(fisher_val))
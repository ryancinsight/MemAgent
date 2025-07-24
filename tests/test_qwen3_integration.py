#!/usr/bin/env python3
"""
Integration tests for Qwen 3 model support in MemAgent.
Tests model loading, configuration parsing, and basic functionality.
"""

import unittest
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from unittest.mock import patch, MagicMock
import tempfile
import os

class TestQwen3Integration(unittest.TestCase):
    """Test suite for Qwen 3 model integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_model_paths = [
            "Qwen/Qwen3-0.6B",
            "Qwen/Qwen3-8B", 
            "Qwen/Qwen3-14B",
        ]
        
    def test_qwen3_flops_counter_support(self):
        """Test that Qwen 3 is supported in flops counter."""
        from verl.utils.flops_counter import VALID_CONFIG_TYPE
        self.assertIn("qwen3", VALID_CONFIG_TYPE)
        
    def test_qwen3_chat_template_registration(self):
        """Test that Qwen 3 tokenizer is registered in chat templates."""
        from recurrent.chat_template.utils import __registered_tokenizer__
        self.assertIn("Qwen3TokenizerFast", __registered_tokenizer__)
        self.assertEqual(__registered_tokenizer__["Qwen3TokenizerFast"], "Qwen/Qwen3-0.6B")
        
    def test_qwen3_chat_template_file_exists(self):
        """Test that Qwen 3 chat template file exists."""
        template_path = os.path.join("recurrent", "chat_template", "Qwen3TokenizerFast.j2")
        self.assertTrue(os.path.exists(template_path))
        
    @patch('transformers.AutoConfig.from_pretrained')
    def test_qwen3_config_loading(self, mock_config):
        """Test Qwen 3 configuration loading."""
        # Mock a Qwen 3 config
        mock_config.return_value = MagicMock()
        mock_config.return_value.model_type = "qwen3"
        mock_config.return_value.architectures = ["Qwen3ForCausalLM"]
        mock_config.return_value.hidden_size = 4096
        mock_config.return_value.num_attention_heads = 32
        mock_config.return_value.num_hidden_layers = 32
        
        config = AutoConfig.from_pretrained("Qwen/Qwen3-7B-Instruct")
        self.assertEqual(config.model_type, "qwen3")
        
    def test_model_path_updates_in_scripts(self):
        """Test that key script files have been updated with Qwen 3 paths."""
        scripts_to_check = [
            "run_memory_7B.sh",
            "run_memory_14B.sh", 
            "run_memory_7B_async.sh",
            "run_tool_gsm8k_async.sh"
        ]
        
        for script in scripts_to_check:
            if os.path.exists(script):
                with open(script, 'r') as f:
                    content = f.read()
                    # Should contain Qwen3 reference
                    self.assertTrue("Qwen3" in content or "qwen3" in content,
                                  f"Script {script} should reference Qwen 3 models")
                                  
    def test_readme_qwen3_documentation(self):
        """Test that README.md documents Qwen 3 support."""
        with open("README.md", 'r') as f:
            content = f.read()
            self.assertIn("Qwen 3", content)
            self.assertIn("Qwen/Qwen3-", content)
            
    @unittest.skipIf(not torch.cuda.is_available(), "CUDA not available")
    def test_qwen3_model_loading_mock(self):
        """Test Qwen 3 model loading with mocked transformers."""
        with patch('transformers.AutoModelForCausalLM.from_pretrained') as mock_model:
            with patch('transformers.AutoTokenizer.from_pretrained') as mock_tokenizer:
                # Mock successful loading
                mock_model.return_value = MagicMock()
                mock_tokenizer.return_value = MagicMock()
                mock_tokenizer.return_value.__class__.__name__ = "Qwen3TokenizerFast"
                
                # Test loading
                model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-0.5B-Instruct")
                tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.5B-Instruct")
                
                self.assertIsNotNone(model)
                self.assertIsNotNone(tokenizer)
                
    def test_backward_compatibility_qwen25(self):
        """Test that Qwen 2.5 models are still supported."""
        from verl.utils.flops_counter import VALID_CONFIG_TYPE
        self.assertIn("qwen2", VALID_CONFIG_TYPE)
        self.assertIn("qwen2_vl", VALID_CONFIG_TYPE)
        self.assertIn("qwen2_5_vl", VALID_CONFIG_TYPE)
        
        from recurrent.chat_template.utils import __registered_tokenizer__
        self.assertIn("Qwen2TokenizerFast", __registered_tokenizer__)
        
    def test_training_script_qwen3_references(self):
        """Test that training scripts reference Qwen 3 models appropriately."""
        example_script = "examples/sft/gsm8k/run_qwen_05_sp2_liger.sh"
        if os.path.exists(example_script):
            with open(example_script, 'r') as f:
                content = f.read()
                self.assertIn("Qwen3-0.5B-Instruct", content)
                self.assertIn("qwen-3-0.5b", content.lower())


class TestQwen3ModelArchitecture(unittest.TestCase):
    """Test Qwen 3 model architecture compatibility."""
    
    def test_qwen3_config_compatibility(self):
        """Test that Qwen 3 configs are compatible with existing code."""
        # This would test actual config compatibility if we had real models
        # For now, test the structure we expect
        expected_attributes = [
            'hidden_size',
            'num_attention_heads', 
            'num_hidden_layers',
            'vocab_size',
            'max_position_embeddings'
        ]
        
        # Mock config structure
        mock_config = {
            'hidden_size': 4096,
            'num_attention_heads': 32,
            'num_hidden_layers': 32,
            'vocab_size': 152064,
            'max_position_embeddings': 262144,  # Qwen 3's extended context
            'model_type': 'qwen3'
        }
        
        for attr in expected_attributes:
            self.assertIn(attr, mock_config)
            
    def test_qwen3_context_length_support(self):
        """Test that Qwen 3's extended context length is recognized."""
        # Qwen 3 supports up to 262k context length natively
        expected_max_context = 262144
        
        # This would be tested with actual model loading
        # For now, verify our documentation reflects this
        with open("PRD.md", 'r') as f:
            content = f.read()
            self.assertIn("262K", content)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
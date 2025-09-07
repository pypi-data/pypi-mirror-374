import pytest
import sys
from unittest.mock import patch, MagicMock
import json

sys.path.insert(0, 'src')
from autocli import parse, AutoCLIArgs


class TestAutoCLIArgs:
    def test_named_access(self):
        args = AutoCLIArgs({'name': 'Alice', 'count': 5})
        assert args.name == 'Alice'
        assert args.count == 5
    
    def test_positional_access(self):
        args = AutoCLIArgs({}, [1, 2, 3])
        assert args[0] == 1
        assert args[1] == 2
        assert args[2] == 3
    
    def test_dict_access(self):
        args = AutoCLIArgs({'name': 'Bob'})
        assert args['name'] == 'Bob'


class TestParser:
    @patch('autocli.parser.T5ForConditionalGeneration')
    @patch('autocli.parser.T5Tokenizer')
    def test_parse_simple_positional(self, mock_tokenizer, mock_model):
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = json.dumps({
            "positional": ["num1", "num2"],
            "named": {},
            "description": "Adds two numbers"
        })
        
        mock_tokenizer_instance.decode.return_value = mock_response
        mock_model_instance.generate.return_value = [[1, 2, 3]]
        mock_tokenizer_instance.return_value = {
            'input_ids': MagicMock(),
            'attention_mask': MagicMock()
        }
        
        description = """
        This app adds two numbers
        
            $ python sum.py 1 2
            3
        """
        
        with patch('sys.argv', ['sum.py', '10', '20']):
            args = parse(description)
            assert args[0] == 10
            assert args[1] == 20
    
    @patch('autocli.parser.T5ForConditionalGeneration')
    @patch('autocli.parser.T5Tokenizer')
    def test_parse_with_named_args(self, mock_tokenizer, mock_model):
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_response = json.dumps({
            "positional": [],
            "named": {
                "name": {
                    "type": "str",
                    "default": "World",
                    "required": False,
                    "long_flag": "--name",
                    "short_flag": "-n"
                }
            },
            "description": "Greets someone"
        })
        
        mock_tokenizer_instance.decode.return_value = mock_response
        mock_model_instance.generate.return_value = [[1, 2, 3]]
        mock_tokenizer_instance.return_value = {
            'input_ids': MagicMock(),
            'attention_mask': MagicMock()
        }
        
        description = """
        This app greets someone
        
            $ python greet.py --name Alice
            Hello, Alice!
        """
        
        args = parse(description, ['--name', 'Bob'])
        assert args.name == 'Bob'
    
    @patch('autocli.parser.T5ForConditionalGeneration')
    @patch('autocli.parser.T5Tokenizer')
    def test_fallback_parser(self, mock_tokenizer, mock_model):
        mock_tokenizer_instance = MagicMock()
        mock_model_instance = MagicMock()
        
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        mock_model.from_pretrained.return_value = mock_model_instance
        
        mock_tokenizer_instance.decode.return_value = "invalid json"
        mock_model_instance.generate.return_value = [[1, 2, 3]]
        mock_tokenizer_instance.return_value = {
            'input_ids': MagicMock(),
            'attention_mask': MagicMock()
        }
        
        description = """
        This app does something
        
            $ python app.py --flag value 123
        """
        
        args = parse(description, ['--flag', 'test', '456'])
        assert args.flag == 'test'
        assert args[0] == 456
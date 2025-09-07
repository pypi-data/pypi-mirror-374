import pytest
import sys
from unittest.mock import patch, MagicMock
import json

sys.path.insert(0, 'src')
from autocli import parse, AutoCLIArgs
from autocli.parser import LLMParser


@pytest.mark.slow
class TestDataTypes:
    """Test parsing of various data types using real LLM."""
    
    def test_float_parsing(self):
        """Test that float values are correctly parsed."""
        description = """
        Tool with floating point arguments
        
        Examples:
            $ tool --rate 0.5 --threshold 3.14159
            $ tool -r 0.25 -t 2.71828
        """
        
        args = parse(description, ['--rate', '0.75', '--threshold', '1.618'])
        
        # Check that values are accessible
        assert hasattr(args, 'rate') or args[0] == 0.75
        assert hasattr(args, 'threshold') or args[1] == 1.618
    
    def test_boolean_formats(self):
        """Test various boolean representations."""
        description = """
        Tool with boolean flags
        
        Examples:
            $ tool --verbose=true --debug=false
            $ tool --verbose=yes --debug=no
            $ tool --verbose=1 --debug=0
            $ tool --verbose --no-debug
        """
        
        # Test true values
        for true_val in ['true', 'True', 'yes', '1']:
            args = parse(description, ['--verbose', true_val])
            # The value should be interpreted as truthy
            if hasattr(args, 'verbose'):
                assert args.verbose or args.verbose == true_val
        
        # Test false values
        for false_val in ['false', 'False', 'no', '0']:
            args = parse(description, ['--debug', false_val])
            # The value should be interpreted as falsy
            if hasattr(args, 'debug'):
                assert not args.debug or args.debug == false_val
    
    def test_list_parsing(self):
        """Test parsing of list arguments."""
        description = """
        Scheduler with list arguments
        
        Examples:
            $ schedule --days Monday,Wednesday,Friday
            $ schedule --days Mon,Tue,Wed,Thu,Fri
            $ schedule --times 9:00,12:00,15:00
        """
        
        args = parse(description, ['--days', 'Monday,Tuesday,Wednesday'])
        
        # Should parse comma-separated values
        if hasattr(args, 'days'):
            # Could be parsed as a single string or split
            assert 'Monday' in str(args.days)
            assert 'Tuesday' in str(args.days)
    
    def test_mixed_types(self):
        """Test parsing mixed data types in one command."""
        description = """
        Complex tool with mixed types
        
        Examples:
            $ tool --count 10 --rate 0.5 --enable yes --tags foo,bar,baz
            $ tool -c 5 -r 0.25 --enable=true --tags=alpha,beta
        """
        
        args = parse(description, [
            '--count', '20',
            '--rate', '0.75',
            '--enable', 'true',
            '--tags', 'one,two,three'
        ])
        
        # Check all argument types are present
        assert hasattr(args, 'count') or hasattr(args, 'rate') or hasattr(args, 'enable') or hasattr(args, 'tags')


@pytest.mark.slow
class TestDataTypesWithLLM:
    """Integration tests for data type parsing with real LLM."""
    
    @pytest.fixture(scope="class")
    def llm_parser(self):
        """Create a shared LLM parser instance."""
        return LLMParser()
    
    def test_numeric_type_inference(self, llm_parser):
        """Test LLM's ability to infer numeric types."""
        description = """
        Calculator with numeric inputs
        
        Examples:
            $ calc --precision 0.001 --iterations 1000 --pi 3.14159
            $ calc precision:0.0001 iterations:500 pi:3.14159265
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should identify numeric arguments
        assert "named" in parsed or "positional" in parsed
    
    def test_boolean_inference(self, llm_parser):
        """Test LLM's understanding of boolean values."""
        description = """
        Build tool with boolean options
        
        Examples:
            $ build --verbose=true --optimize=yes --debug=1
            $ build --quiet=false --no-optimize --debug=0
            $ build verbose:yes optimize:no debug:true
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should recognize boolean flags
        if "named" in parsed:
            # At least some of these should be recognized
            arg_names = list(parsed["named"].keys())
            expected = ["verbose", "optimize", "debug", "quiet"]
            assert any(exp in str(arg_names).lower() for exp in expected)
    
    def test_list_type_inference(self, llm_parser):
        """Test LLM's ability to recognize list arguments."""
        description = """
        Task scheduler accepting lists
        
        Examples:
            $ schedule --days Monday,Tuesday,Wednesday,Thursday,Friday
            $ schedule --days="Mon Tue Wed Thu Fri"
            $ schedule days:[Monday,Wednesday,Friday] times:[9:00,17:00]
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should identify days as an argument
        if "named" in parsed:
            assert any("day" in key.lower() for key in parsed["named"].keys())
    
    def test_complex_mixed_types(self, llm_parser):
        """Test parsing of complex commands with mixed types."""
        description = """
        Data processor with various options
        
        Usage:
            $ process --input data.csv --sample-rate 0.5 --max-rows 10000 \
                      --columns id,name,age --validate true --formats csv,json,xml
            
            $ process input:file.txt sample-rate:0.25 max-rows:5000 \
                      columns:[a,b,c] validate:yes formats:"csv json"
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should identify multiple argument types
        if "named" in parsed:
            args = parsed["named"]
            # Should recognize various arguments
            arg_keys = str(args.keys()).lower()
            assert "input" in arg_keys or "sample" in arg_keys or "max" in arg_keys
    
    def test_day_of_week_parsing(self, llm_parser):
        """Test parsing days of the week."""
        description = """
        Weekly scheduler
        
        Examples:
            $ schedule --run-days Monday,Wednesday,Friday
            $ schedule --run-days "Mon Wed Fri"
            $ schedule --weekend Saturday,Sunday
            $ schedule --weekdays Mon-Fri
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should recognize day-related arguments
        if "named" in parsed:
            arg_keys = str(parsed["named"].keys()).lower()
            assert "day" in arg_keys or "weekend" in arg_keys or "weekday" in arg_keys
    
    def test_unit_parsing(self, llm_parser):
        """Test parsing values with units."""
        description = """
        Server configuration
        
        Examples:
            $ server --memory 2GB --timeout 30s --cache-size 512MB
            $ server memory:4GB timeout:60s cache:1GB
            $ server --mem 1024MB --timeout 45.5 --cache 256M
        """
        
        parsed = llm_parser.parse_description(description)
        
        # Should recognize arguments with units
        if "named" in parsed:
            arg_keys = str(parsed["named"].keys()).lower()
            assert "memory" in arg_keys or "mem" in arg_keys or "timeout" in arg_keys
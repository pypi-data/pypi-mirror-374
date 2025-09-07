import pytest
import sys

sys.path.insert(0, 'src')
from autocli import parse, AutoCLIArgs
from autocli.parser import LLMParser


@pytest.mark.slow
class TestRealLLMIntegration:
    """Integration tests that use the actual LLM model (slow)."""
    
    @pytest.fixture(scope="class")
    def llm_parser(self):
        """Create a shared LLM parser instance for all tests."""
        return LLMParser()
    
    def test_parse_simple_addition(self, llm_parser):
        """Test parsing a simple addition CLI app."""
        description = """
        This application adds two numbers together and prints the result.
        
        Example:
            $ python add.py 5 10
            15
        """
        
        parsed = llm_parser.parse_description(description)
        
        assert "positional" in parsed
        assert len(parsed["positional"]) >= 2 or "arg0" in parsed.get("positional", [])
        assert "description" in parsed
    
    def test_parse_named_arguments(self, llm_parser):
        """Test parsing named arguments with defaults."""
        description = """
        A greeting application that welcomes users with customizable messages.
        
        Examples:
            $ python greet.py --name Alice --greeting "Good morning"
            Good morning, Alice!
            
            $ python greet.py --name Bob
            Hello, Bob!
        """
        
        parsed = llm_parser.parse_description(description)
        
        assert "named" in parsed
        named_args = parsed.get("named", {})
        
        # Check if name argument was detected
        assert any("name" in key.lower() for key in named_args.keys())
    
    def test_parse_mixed_arguments(self, llm_parser):
        """Test parsing both positional and named arguments."""
        description = """
        File processor that reads a file and optionally filters lines.
        
        Usage:
            $ python process.py input.txt --filter "error" --output result.txt
            Processed 42 lines, found 5 matches
            
            $ python process.py data.csv
            Processed 100 lines
        """
        
        parsed = llm_parser.parse_description(description)
        
        assert "positional" in parsed
        assert "named" in parsed
        assert len(parsed.get("positional", [])) >= 1
        
        named_args = parsed.get("named", {})
        assert any("filter" in key.lower() or "output" in key.lower() 
                  for key in named_args.keys())
    
    def test_parse_numeric_arguments(self, llm_parser):
        """Test parsing with numeric type inference."""
        description = """
        Server application that starts on a specified port.
        
        Examples:
            $ python server.py --port 8080 --workers 4 --timeout 30.5
            Server started on port 8080 with 4 workers
        """
        
        parsed = llm_parser.parse_description(description)
        
        named_args = parsed.get("named", {})
        
        # Check if numeric arguments were detected
        assert any("port" in key.lower() for key in named_args.keys())
        assert any("workers" in key.lower() for key in named_args.keys())
    
    def test_parse_boolean_flags(self, llm_parser):
        """Test parsing boolean flag arguments."""
        description = """
        Build tool with various options.
        
        Usage:
            $ python build.py --verbose --clean --debug
            Building in debug mode with verbose output
            
            $ python build.py --release
            Building release version
        """
        
        parsed = llm_parser.parse_description(description)
        
        named_args = parsed.get("named", {})
        
        # Check if boolean flags were detected
        flag_names = ["verbose", "clean", "debug", "release"]
        assert any(any(flag in key.lower() for flag in flag_names) 
                  for key in named_args.keys())
    
    def test_end_to_end_positional(self):
        """Test end-to-end parsing with positional arguments."""
        description = """
        Calculator that multiplies two numbers.
        
        Example:
            $ python multiply.py 6 7
            42
        """
        
        args = parse(description, ["3", "4"])
        
        # Should be able to access positional arguments
        assert args[0] == 3
        assert args[1] == 4
    
    def test_end_to_end_named(self):
        """Test end-to-end parsing with named arguments."""
        description = """
        Configuration printer that shows settings.
        
        Example:
            $ python config.py --host localhost --port 8080
            Connecting to localhost:8080
        """
        
        args = parse(description, ["--host", "example.com", "--port", "3000"])
        
        # Should be able to access named arguments
        assert hasattr(args, 'host') or hasattr(args, 'HOST')
        if hasattr(args, 'host'):
            assert args.host == "example.com"
        if hasattr(args, 'port'):
            assert args.port == "3000" or args.port == 3000
    
    def test_complex_real_world_example(self, llm_parser):
        """Test a complex real-world CLI description."""
        description = """
        Database migration tool that manages schema updates.
        
        Usage:
            migrate.py [command] [options]
        
        Commands:
            up      Apply pending migrations
            down    Rollback last migration
            status  Show migration status
        
        Options:
            --database DATABASE    Database connection string
            --dry-run             Show what would be done without executing
            --force               Skip confirmation prompts
            --verbose             Show detailed output
            --limit N             Limit number of migrations to apply
        
        Examples:
            $ python migrate.py up --database postgresql://localhost/mydb
            Applied 3 migrations
            
            $ python migrate.py down --limit 1 --dry-run
            Would rollback: 001_create_users_table
            
            $ python migrate.py status --database mysql://localhost/app
            5 migrations applied, 2 pending
        """
        
        parsed = llm_parser.parse_description(description)
        
        assert "positional" in parsed or "named" in parsed
        
        # Should detect at least some of the documented options
        if "named" in parsed:
            named_args = parsed.get("named", {})
            common_args = ["database", "dry", "force", "verbose", "limit"]
            assert any(any(arg in key.lower() for arg in common_args) 
                      for key in named_args.keys())
    
    def test_fallback_on_invalid_llm_output(self, llm_parser):
        """Test that fallback parser is used when LLM fails."""
        # Force a fallback by mocking the model to return invalid JSON
        import json
        from unittest.mock import patch
        
        with patch.object(llm_parser, 'model') as mock_model:
            mock_model.generate.side_effect = Exception("Model error")
            
            description = """
            Simple app example
            
            $ python app.py --flag value 123
            """
            
            parsed = llm_parser.parse_description(description)
            
            # Fallback parser should still extract basic info
            assert "positional" in parsed
            assert "named" in parsed
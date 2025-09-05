# Function Auditor 🔍 - Developer Documentation

A comprehensive tool for auditing unused functions in codebases across multiple programming languages. This document provides detailed information for developers working with or extending the Function Auditor.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This tool was last updated on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📦 Project Structure

```
function_auditor/
├── __init__.py              # Package interface and version info
├── main.py                  # ScriptCraft BaseTool integration
├── function_auditor.py      # Core auditing logic
├── env.py                   # Dual-environment support
├── audit_functions_cli.py   # Legacy CLI wrapper
├── example_usage.py         # Usage examples
├── README.md               # User documentation
├── README_devs.md          # This developer documentation
└── README_distributable.md # Distributable documentation
```

---

## 🚀 Development Usage

### Command Line (Development)
```bash
# Run from ScriptCraft workspace
python -m scriptcraft.tools.function_auditor.main --input_paths file.py --mode single

# Run with specific language
python -m scriptcraft.tools.function_auditor.main --mode batch --language python --folder src

# Run with pattern matching
python -m scriptcraft.tools.function_auditor.main --mode batch --pattern "**/*.py" --language python
```

### Python API (Development)
```python
from scriptcraft.tools.function_auditor import FunctionAuditor, BatchFunctionAuditor

# Single file audit
auditor = FunctionAuditor("path/to/file.py", language="python")
result = auditor.audit_functions()
auditor.generate_report(result)

# Batch audit
batch_auditor = BatchFunctionAuditor(language="python")
files = batch_auditor.get_files_by_extension("py", "src")
results = batch_auditor.audit_files(files)
batch_auditor.generate_batch_report(results)
```

---

## ⚙️ Core Components

### FunctionAuditor Class
- **Purpose**: Audits individual files for unused functions
- **Key Methods**:
  - `extract_functions()`: Extract function definitions using language-specific patterns
  - `search_function_usage()`: Search for function usage across codebase
  - `audit_functions()`: Perform complete audit
  - `generate_report()`: Generate detailed report

### BatchFunctionAuditor Class
- **Purpose**: Batch processing of multiple files
- **Key Methods**:
  - `get_files_by_extension()`: Get files by extension
  - `get_files_in_folder()`: Get files in specific folder
  - `get_files_by_pattern()`: Get files matching glob pattern
  - `audit_files()`: Audit multiple files
  - `generate_batch_report()`: Generate comprehensive report

### FunctionAuditorTool Class
- **Purpose**: ScriptCraft BaseTool integration
- **Inherits**: `cu.BaseTool`
- **Key Features**:
  - Dual-environment support
  - Standardized argument parsing
  - Integrated logging
  - Output management

---

## 🔧 Language Support

### Adding New Language Support

To add support for a new programming language:

1. **Update Language Configuration** in `function_auditor.py`:
```python
def _get_language_config(self) -> Dict[str, Any]:
    configs = {
        # ... existing languages ...
        'new_language': {
            'function_pattern': r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            'file_extensions': ['.new'],
            'builtin_functions': ['main', 'init'],
            'private_prefix': '_',
            'project_indicators': ['config.new', 'setup.new']
        }
    }
```

2. **Update Language Detection**:
```python
def _detect_language(self) -> str:
    extension = self.target_file.suffix.lower()
    language_map = {
        # ... existing mappings ...
        '.new': 'new_language'
    }
```

3. **Test the Implementation**:
```python
# Test single file
auditor = FunctionAuditor("test.new", language="new_language")
result = auditor.audit_functions()

# Test batch processing
batch_auditor = BatchFunctionAuditor(language="new_language")
files = batch_auditor.get_files_by_extension("new", "src")
```

---

## 🧪 Testing

### Unit Tests
```bash
# Run function auditor tests
python -m pytest tests/tools/test_function_auditor.py -v

# Run with coverage
python -m pytest tests/tools/test_function_auditor.py --cov=scriptcraft.tools.function_auditor
```

### Integration Tests
```bash
# Test with real codebases
python -m pytest tests/integration/test_function_auditor_integration.py -v
```

### Manual Testing
```bash
# Test with sample files
python -m scriptcraft.tools.function_auditor.main --input_paths tests/data/sample.py --mode single

# Test batch processing
python -m scriptcraft.tools.function_auditor.main --mode batch --language python --folder tests/data
```

---

## 🔄 Dependencies

### Core Dependencies
- `pathlib`: File path handling
- `re`: Regular expression pattern matching
- `typing`: Type hints
- `scriptcraft.common`: BaseTool and common utilities

### Optional Dependencies
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting

---

## 🚨 Error Handling

### Common Error Scenarios

1. **File Not Found**
   - **Cause**: Target file doesn't exist
   - **Solution**: Validate file existence before processing

2. **Language Detection Failure**
   - **Cause**: Unsupported file extension
   - **Solution**: Default to Python or provide explicit language parameter

3. **Pattern Matching Issues**
   - **Cause**: Incorrect regex patterns for function detection
   - **Solution**: Test patterns with sample files and adjust as needed

4. **Project Root Detection**
   - **Cause**: Missing project indicators
   - **Solution**: Fall back to current directory or provide explicit project root

### Error Recovery Strategies

```python
try:
    auditor = FunctionAuditor(file_path, language=language)
    result = auditor.audit_functions()
except FileNotFoundError:
    print(f"❌ File not found: {file_path}")
    return None
except Exception as e:
    print(f"⚠️ Error auditing {file_path}: {e}")
    return None
```

---

## 📊 Performance Considerations

### Optimization Tips

1. **File Processing**
   - Process files in parallel for large codebases
   - Use lazy loading for large files
   - Cache function extraction results

2. **Pattern Matching**
   - Compile regex patterns once and reuse
   - Use efficient regex patterns
   - Consider using AST parsing for better accuracy

3. **Memory Usage**
   - Process files one at a time for large batches
   - Clear intermediate results
   - Use generators for large result sets

### Performance Monitoring

```python
import time
import psutil

def audit_with_monitoring(files):
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    results = batch_auditor.audit_files(files)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    print(f"⏱️ Processing time: {end_time - start_time:.2f}s")
    print(f"💾 Memory usage: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
    
    return results
```

---

## 🔧 Configuration

### Tool Configuration

The Function Auditor can be configured via the ScriptCraft configuration system:

```yaml
# config.yaml
tools:
  function_auditor:
    default_language: "python"
    supported_languages:
      - "python"
      - "gdscript"
      - "javascript"
      - "typescript"
      - "java"
      - "cpp"
      - "csharp"
    batch_size: 100
    max_file_size: 10485760  # 10MB
```

### Environment Variables

```bash
# Override default language
export FUNCTION_AUDITOR_DEFAULT_LANGUAGE=python

# Set batch size
export FUNCTION_AUDITOR_BATCH_SIZE=50

# Enable debug mode
export FUNCTION_AUDITOR_DEBUG=true
```

---

## 📋 Development Checklist

### 1. Code Quality ⬜
- [ ] Type hints for all functions
- [ ] Docstrings for all public methods
- [ ] Error handling for edge cases
- [ ] Input validation
- [ ] Performance optimization

### 2. Testing ⬜
- [ ] Unit tests for core functionality
- [ ] Integration tests with real codebases
- [ ] Edge case testing
- [ ] Performance testing
- [ ] Error condition testing

### 3. Documentation ⬜
- [ ] API documentation
- [ ] Usage examples
- [ ] Configuration guide
- [ ] Troubleshooting guide
- [ ] Performance tuning guide

### 4. Integration ⬜
- [ ] ScriptCraft BaseTool integration
- [ ] Dual-environment support
- [ ] Console script entry point
- [ ] Package metadata
- [ ] Distribution testing

---

## 🤝 Contributing

### Development Workflow

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/ScriptCraft-Workspace.git
   cd ScriptCraft-Workspace
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/function-auditor-enhancement
   ```

3. **Make Changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation

4. **Test Changes**
   ```bash
   python -m pytest tests/tools/test_function_auditor.py
   python -m scriptcraft.tools.function_auditor.main --help
   ```

5. **Submit Pull Request**
   - Include description of changes
   - Reference any related issues
   - Ensure all tests pass

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Write descriptive docstrings
- Use meaningful variable and function names
- Keep functions focused and single-purpose

### Testing Requirements

- All new functionality must have unit tests
- Integration tests for major features
- Performance tests for optimization changes
- Error handling tests for edge cases

---

## 📞 Support

### Getting Help

- **Documentation**: Check this README and the main README.md
- **Issues**: Create an issue on GitHub for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas

### Reporting Bugs

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - ScriptCraft version
   - Operating system

2. **Reproduction Steps**
   - Clear steps to reproduce the issue
   - Sample code or files that trigger the bug

3. **Expected vs Actual Behavior**
   - What you expected to happen
   - What actually happened

4. **Error Messages**
   - Full error traceback
   - Any relevant log output

### Feature Requests

When requesting features, please include:

1. **Use Case**
   - Why is this feature needed?
   - How would it be used?

2. **Proposed Implementation**
   - High-level approach
   - Any relevant examples

3. **Alternatives Considered**
   - Other ways to solve the problem
   - Why this approach is preferred

---

## 📝 Changelog

### Version 1.0.0 (Current)
- Initial release with multi-language support
- Python, GDScript, JavaScript, TypeScript, Java, C++, C# support
- Batch processing capabilities
- ScriptCraft integration
- Console script entry point

### Planned Features
- Additional language support (Go, Rust, Swift)
- IDE plugin integration
- Automated refactoring suggestions
- Performance optimization recommendations
- CI/CD pipeline integration

---

## 📚 Additional Resources

- [ScriptCraft Documentation](https://github.com/mcusac/ScriptCraft-Workspace#readme)
- [Python Regular Expressions](https://docs.python.org/3/library/re.html)
- [Pathlib Documentation](https://docs.python.org/3/library/pathlib.html)
- [Type Hints Guide](https://docs.python.org/3/library/typing.html)

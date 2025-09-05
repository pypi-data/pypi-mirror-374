# Function Auditor 🔍

A comprehensive tool for auditing unused functions in codebases across multiple programming languages. Provides detailed analysis reports and cleanup recommendations.

## Features

- **Multi-Language Support**: Python, GDScript, JavaScript, TypeScript, Java, C++, C#
- **Individual File Auditing**: Audit single files for unused functions
- **Batch Processing**: Audit entire folders or projects at once
- **Smart Function Detection**: Identifies function definitions and usage patterns
- **Comprehensive Reporting**: Detailed reports with usage statistics and recommendations
- **Flexible Output**: Support for summary-only and unused-only modes
- **DRY Architecture**: Reusable components that avoid code duplication

## Installation

The Function Auditor is included in the ScriptCraft Python package. Install via:

```bash
pip install scriptcraft-python
```

## Usage

### As a Python Module

```python
from scriptcraft.tools.function_auditor import FunctionAuditor, BatchFunctionAuditor

# Audit a single Python file
auditor = FunctionAuditor("path/to/file.py", language="python")
result = auditor.audit_functions()
auditor.generate_report(result)

# Audit a GDScript file
auditor = FunctionAuditor("path/to/file.gd", language="gdscript")
result = auditor.audit_functions()

# Batch audit multiple files
batch_auditor = BatchFunctionAuditor(language="python")
files = batch_auditor.get_files_by_extension("py", "src")
results = batch_auditor.audit_files(files)
batch_auditor.generate_batch_report(results)
```

### As a CLI Tool

```bash
# Using the console script (after pip install)
function-auditor --input_paths file.py --mode single

# Audit single file
python -m scriptcraft.tools.function_auditor.main --input_paths file.py --mode single

# Batch audit all Python files
python -m scriptcraft.tools.function_auditor.main --mode batch --language python

# Batch audit specific folder
python -m scriptcraft.tools.function_auditor.main --mode batch --folder src --language python

# Batch audit files matching a pattern
python -m scriptcraft.tools.function_auditor.main --mode batch --pattern "**/*.py" --language python

# Show detailed unused functions report
python -m scriptcraft.tools.function_auditor.main --mode batch --detailed_unused --language python

# Summary only (no detailed output)
python -m scriptcraft.tools.function_auditor.main --mode batch --summary_only --language python
```

## API Reference

### FunctionAuditor

Main class for auditing individual files across multiple programming languages.

#### Constructor
- `FunctionAuditor(target_file: str, language: Optional[str] = None)`: Initialize auditor for a specific file

#### Methods

- `extract_functions()`: Extract all function definitions from the target file
- `search_function_usage(func_name)`: Search for usage of a specific function
- `audit_functions(verbose=True)`: Perform complete audit
- `generate_report(audit_result, verbose=True)`: Generate detailed report

### BatchFunctionAuditor

Class for batch processing multiple files across multiple programming languages.

#### Constructor
- `BatchFunctionAuditor(project_root: Optional[str] = None, language: Optional[str] = None)`: Initialize batch auditor

#### Methods

- `get_files_in_folder(folder_path)`: Get all files with language-specific extensions in a specific folder
- `get_files_by_extension(extension, base_folder)`: Get files by extension in base folder
- `get_files_by_pattern(pattern, base_folder)`: Get files matching glob pattern
- `get_all_files()`: Get all files with language-specific extensions in the project
- `audit_files(files, show_details=True, unused_only=False, verbose=True)`: Audit multiple files
- `generate_batch_report(results, verbose=True)`: Generate comprehensive batch report
- `get_unused_functions_list(results)`: Get flat list of all unused functions
- `generate_unused_functions_report(results, verbose=True)`: Generate detailed unused functions report

## Supported Languages

The Function Auditor supports the following programming languages:

### Python
- **Extensions**: `.py`
- **Function Pattern**: `def function_name(`
- **Built-in Functions**: `__init__`, `__str__`, `__repr__`, etc.
- **Project Indicators**: `setup.py`, `pyproject.toml`, `requirements.txt`

### GDScript
- **Extensions**: `.gd`
- **Function Pattern**: `func function_name(`
- **Built-in Functions**: `_ready`, `_process`, `_input`, etc.
- **Project Indicators**: `project.godot`

### JavaScript
- **Extensions**: `.js`
- **Function Pattern**: `function name(` or `const name = function`
- **Project Indicators**: `package.json`, `node_modules`

### TypeScript
- **Extensions**: `.ts`
- **Function Pattern**: `function name(` or `const name = (`
- **Project Indicators**: `package.json`, `tsconfig.json`

### Java
- **Extensions**: `.java`
- **Function Pattern**: `public/private function_name(`
- **Built-in Functions**: `main`, `toString`, `equals`
- **Project Indicators**: `pom.xml`, `build.gradle`

### C++
- **Extensions**: `.cpp`, `.c`, `.h`, `.hpp`
- **Function Pattern**: `return_type function_name(`
- **Built-in Functions**: `main`
- **Project Indicators**: `CMakeLists.txt`, `Makefile`

### C#
- **Extensions**: `.cs`
- **Function Pattern**: `public/private function_name(`
- **Built-in Functions**: `Main`, `ToString`, `Equals`
- **Project Indicators**: `.csproj`, `.sln`

## Output

The auditor provides:

- **Function Counts**: Total functions, used functions, unused functions
- **Usage Statistics**: Where functions are used across the codebase
- **Recommendations**: Suggestions for handling unused functions
- **File Summaries**: Quick overview of each file's status

## Architecture

The Function Auditor follows the DRY (Don't Repeat Yourself) principle:

- `FunctionAuditor`: Core auditing logic for individual files
- `BatchFunctionAuditor`: Batch processing that reuses `FunctionAuditor`
- `FunctionAuditorTool`: ScriptCraft BaseTool integration
- `main.py`: CLI wrapper that imports and uses the tool

This design ensures that the core auditing logic is written once and reused across different interfaces.

## Integration with ScriptCraft

The Function Auditor is fully integrated into the ScriptCraft Python package:

1. **Modular Design**: Clean separation of concerns
2. **Reusable Components**: Core functionality can be imported and used
3. **Flexible Interface**: Supports both programmatic and CLI usage
4. **Multi-Environment Support**: Works in both development and distributable modes
5. **Comprehensive Documentation**: Clear API and usage examples

## Future Enhancements

- Support for additional programming languages (Go, Rust, Swift, etc.)
- Integration with IDE plugins
- Automated refactoring suggestions
- Performance optimization recommendations
- Code quality metrics
- Integration with CI/CD pipelines

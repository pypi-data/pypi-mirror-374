# Function Auditor 🔍

Automatically analyze codebases to identify unused functions and provide cleanup recommendations. Supports multiple programming languages and generates detailed analysis reports.

---

📅 **Build Date:** [INSERT_DATE_HERE]

This build was packaged on the date above.  
For reproducibility and support, always refer to this date when sharing logs or output.

---

## 📂 Directory Structure

```
function_auditor_distributable/
├── input/                  # Place your code files here
├── output/                # Generated analysis reports
├── logs/                  # Execution logs
├── scripts/               # Core implementation (no need to modify)
├── embed_py311/          # Embedded Python environment
├── config.bat            # Configuration settings
└── run.bat              # Start the function auditor
```

---

## 🚀 Quick Start

1. **Prepare your code**:
   - Place code files in `input/` directory
   - Supported languages: Python, GDScript, JavaScript, TypeScript, Java, C++, C#
   - Use any supported file format (`.py`, `.gd`, `.js`, `.ts`, `.java`, `.cpp`, `.cs`)
2. **Double-click `run.bat`**
3. **Check results** in `output/`:
   - Analysis reports with unused function details
   - Recommendations for code cleanup
   - Summary statistics

---

## 📋 Requirements

- Windows 10 or later
- 4GB RAM minimum
- 1GB free disk space
- Files must be:
  - Supported programming language format
  - Not password protected
  - Under 50MB each
  - Properly encoded (UTF-8 recommended)

---

## ⚙️ Configuration

Default settings work for most cases, but you can customize:

1. **Language Settings**
   - Default programming language
   - File extension mappings
   - Function pattern recognition

2. **Analysis Settings**
   - Batch processing size
   - Maximum file size
   - Output format preferences

3. **Output Settings**
   - Report format (JSON, text)
   - Detail level (summary, detailed, unused-only)
   - File naming conventions

---

## 📊 Example Usage

### Basic Function Analysis
1. Copy Python files to `input/`
2. Run the auditor
3. Open analysis reports from `output/`
4. Review unused function recommendations

### Multi-Language Analysis
1. Place files from different languages in `input/`
2. Run the auditor
3. Get language-specific analysis reports
4. Compare unused functions across languages

### Batch Processing
1. Organize files by language in subdirectories
2. Run the auditor
3. Get comprehensive analysis across entire codebase
4. Export results for further processing

---

## 🔎 Troubleshooting

### Common Issues

1. **"No Files Found"**
   - Symptom: No input files detected
   - Solution: Add supported language files to input/ folder

2. **"Unsupported Language"**
   - Symptom: Language not recognized
   - Solution: Ensure file has supported extension (.py, .gd, .js, etc.)

3. **"Analysis Failed"**
   - Symptom: Processing error for specific files
   - Solution: Check file encoding and syntax validity

4. **"Memory Error"**
   - Symptom: Out of memory during processing
   - Solution: Reduce batch size or process smaller files

### Error Messages

- `[FA001]`: No supported files found in input directory
- `[FA002]`: Unsupported file format or language
- `[FA003]`: File processing error
- `[FA004]`: Analysis generation failed
- `[FA005]`: Output directory creation failed

### Performance Issues

- **Large Files**: Files over 10MB may take longer to process
- **Many Files**: Processing 1000+ files may require more memory
- **Complex Code**: Nested functions and complex patterns may slow analysis

---

## 📞 Support

### Getting Help

- Check `logs/run_log.txt` for detailed error information
- Contact: scriptcraft@example.com
- Hours: Monday-Friday, 9am-5pm CST
- Response time: Within 1 business day

### Common Solutions

1. **File Encoding Issues**
   - Ensure files are UTF-8 encoded
   - Check for special characters in file paths
   - Verify file permissions

2. **Language Detection Problems**
   - Use standard file extensions
   - Avoid non-standard naming conventions
   - Check file content for language-specific syntax

3. **Performance Optimization**
   - Process files in smaller batches
   - Use SSD storage for better I/O performance
   - Close other applications to free memory

---

## 📝 Release Notes

### Current Version (1.0.0)
- Multi-language support (Python, GDScript, JavaScript, TypeScript, Java, C++, C#)
- Batch processing capabilities
- Detailed analysis reports
- Unused function identification
- Cleanup recommendations
- JSON and text output formats

### Known Issues
- Large files (>50MB) may cause memory issues
- Complex regex patterns may slow processing
- Some edge cases in function detection
- Workaround: Process large files individually or in smaller batches

### Performance Notes
- Processing speed: ~100 files per minute (varies by file size)
- Memory usage: ~200MB base + ~1MB per file
- Disk usage: ~50MB for tool + output files

---

## 🔧 Advanced Usage

### Custom Configuration

You can modify the configuration by editing `config.bat`:

```batch
REM Set default language
set DEFAULT_LANGUAGE=python

REM Set batch size
set BATCH_SIZE=50

REM Set output format
set OUTPUT_FORMAT=json

REM Enable debug mode
set DEBUG_MODE=false
```

### Command Line Options

For advanced users, you can run the tool directly:

```batch
cd scripts
python main.py --help
```

Available options:
- `--input_paths`: Specify input files or directories
- `--mode`: Analysis mode (single, batch, folder, pattern)
- `--language`: Programming language to analyze
- `--output_dir`: Output directory for results
- `--summary_only`: Show only summary results
- `--unused_only`: Show only unused functions
- `--detailed_unused`: Show detailed unused function report

### Batch Processing Examples

```batch
REM Analyze all Python files
python main.py --mode batch --language python

REM Analyze specific folder
python main.py --mode batch --folder input/src --language python

REM Analyze files matching pattern
python main.py --mode batch --pattern "**/*.py" --language python

REM Generate detailed unused function report
python main.py --mode batch --detailed_unused --language python
```

---

## 📊 Output Formats

### JSON Output
```json
{
  "summary": {
    "total_functions": 150,
    "used_functions": 120,
    "unused_functions": 30,
    "unused_percentage": 20.0
  },
  "files": [
    {
      "file": "src/main.py",
      "unused_count": 5,
      "total_count": 25,
      "unused_functions": [
        {
          "name": "unused_function",
          "line": 45,
          "language": "python"
        }
      ]
    }
  ]
}
```

### Text Output
```
Function Audit Report
====================
Total functions: 150
Used functions: 120
Unused functions: 30
Unused percentage: 20.0%

Files with unused functions:
- src/main.py (5 unused)
- src/utils.py (3 unused)
- src/helpers.py (2 unused)

Detailed unused functions:
src/main.py:
  - unused_function (line 45)
  - helper_function (line 67)
  - debug_function (line 89)
```

---

## 🚀 Tips for Best Results

### File Organization
- Keep related files in the same directory
- Use consistent naming conventions
- Avoid deeply nested directory structures

### Code Quality
- Use clear function names
- Follow language-specific conventions
- Avoid overly complex function signatures

### Analysis Strategy
- Start with small batches to test configuration
- Process by language for better accuracy
- Review results before making changes
- Keep backups of original code

### Performance Optimization
- Process files during off-peak hours
- Use SSD storage for better performance
- Close unnecessary applications
- Monitor system resources during processing

---

## 📚 Additional Resources

- [Supported Languages Guide](README.md#supported-languages)
- [API Reference](README.md#api-reference)
- [Troubleshooting Guide](#troubleshooting)
- [Performance Tips](#performance-optimization)

---

## 🔄 Updates and Maintenance

### Checking for Updates
- Visit the ScriptCraft website for latest versions
- Check release notes for new features and bug fixes
- Backup your configuration before updating

### Maintenance Tasks
- Clean output directory regularly
- Archive old analysis reports
- Update configuration as needed
- Monitor disk space usage

### Backup Recommendations
- Keep copies of important analysis results
- Backup configuration files
- Archive input files for future reference
- Document any custom modifications

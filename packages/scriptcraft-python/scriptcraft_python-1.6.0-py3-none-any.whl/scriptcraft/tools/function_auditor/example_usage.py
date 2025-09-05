#!/usr/bin/env python3
"""
Example usage of the ScriptCraft Function Auditor Plugin
This shows how to use the plugin programmatically in your own Python scripts.
"""

import sys
from pathlib import Path

# Add the function_auditor directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from function_auditor import FunctionAuditor, BatchFunctionAuditor

def example_single_file_audit():
    """Example: Audit a single file"""
    print("🔍 Example: Single File Audit")
    print("=" * 50)
    
    # Audit a specific file
    auditor = FunctionAuditor("scripts/Managers/Construction/BuildingManager.gd")
    result = auditor.audit_functions(verbose=False)  # Set to True for detailed output
    
    print(f"Found {len(result['unused'])} unused functions")
    for func in result['unused']:
        print(f"  ❌ {func['name']} (line {func['line']})")
    print()

def example_batch_audit():
    """Example: Batch audit with flexible file selection"""
    print("🔍 Example: Batch Audit")
    print("=" * 50)
    
    batch_auditor = BatchFunctionAuditor()
    
    # Method 1: Audit all files in a specific folder
    print("Method 1: Audit specific folder")
    files = batch_auditor.get_files_in_folder("scripts/Managers/Construction")
    results = batch_auditor.audit_files(files, show_details=False, verbose=False)
    print(f"Audited {results['files_audited']} files, found {results['total_unused']} unused functions")
    print()
    
    # Method 2: Audit files matching a pattern
    print("Method 2: Audit files matching pattern")
    files = batch_auditor.get_files_by_pattern("**/*Manager*.gd", "scripts")
    results = batch_auditor.audit_files(files, show_details=False, verbose=False)
    print(f"Audited {results['files_audited']} files, found {results['total_unused']} unused functions")
    print()
    
    # Method 3: Audit files by extension
    print("Method 3: Audit files by extension")
    files = batch_auditor.get_files_by_extension("gd", "scripts")
    results = batch_auditor.audit_files(files, show_details=False, verbose=False)
    print(f"Audited {results['files_audited']} files, found {results['total_unused']} unused functions")
    print()

def example_get_unused_functions():
    """Example: Get structured data about unused functions"""
    print("🔍 Example: Get Unused Functions Data")
    print("=" * 50)
    
    batch_auditor = BatchFunctionAuditor()
    
    # Audit a small set of files
    files = batch_auditor.get_files_in_folder("scripts/Managers/Construction")
    results = batch_auditor.audit_files(files, show_details=False, verbose=False)
    
    # Get structured data about unused functions
    unused_functions = batch_auditor.get_unused_functions_list(results)
    
    print(f"Found {len(unused_functions)} unused functions:")
    for func in unused_functions:
        print(f"  📁 {func['file']}")
        print(f"     ❌ {func['function']} (line {func['line']})")
    print()

def example_custom_project():
    """Example: Audit a different project structure"""
    print("🔍 Example: Custom Project Structure")
    print("=" * 50)
    
    # You can specify a different project root
    # batch_auditor = BatchFunctionAuditor("/path/to/other/project")
    
    # Or audit different file types
    batch_auditor = BatchFunctionAuditor()
    
    # Audit Python files instead of GDScript
    files = batch_auditor.get_files_by_extension("py", ".")
    if files:
        results = batch_auditor.audit_files(files, show_details=False, verbose=False)
        print(f"Found {len(files)} Python files, {results['total_unused']} unused functions")
    else:
        print("No Python files found in current directory")
    print()

def main():
    """Run all examples"""
    print("🚀 ScriptCraft Function Auditor Plugin Examples")
    print("=" * 60)
    print()
    
    try:
        example_single_file_audit()
        example_batch_audit()
        example_get_unused_functions()
        example_custom_project()
        
        print("✅ All examples completed successfully!")
        print()
        print("💡 Integration Tips:")
        print("  • Use verbose=False for programmatic usage")
        print("  • Use get_unused_functions_list() for structured data")
        print("  • Use get_files_by_pattern() for flexible file selection")
        print("  • Use get_files_by_extension() for different file types")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("💡 Make sure you're running this from the project root directory")

if __name__ == "__main__":
    main()

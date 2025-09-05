#!/usr/bin/env python3
"""
ScriptCraft Function Auditor Plugin
A comprehensive tool for auditing unused functions in codebases.

This plugin provides both individual file auditing and batch processing capabilities
for finding unused functions across entire codebases. Supports multiple programming languages.

Usage:
    from scriptcraft.tools.function_auditor import FunctionAuditor, BatchFunctionAuditor
    
    # Audit a single file
    auditor = FunctionAuditor("path/to/file.py")
    result = auditor.audit_functions()
    
    # Batch audit multiple files
    batch_auditor = BatchFunctionAuditor()
    files = batch_auditor.get_files_by_extension("py", "src")
    results = batch_auditor.audit_files(files)
"""

import os
import re
import sys
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional

class FunctionAuditor:
    """
    Audits individual files for unused functions across multiple programming languages.
    
    This class extracts function definitions and searches for their usage
    across the entire codebase to identify potentially unused functions.
    Supports Python, GDScript, JavaScript, TypeScript, Java, C++, and C#.
    """
    
    def __init__(self, target_file: str, language: Optional[str] = None):
        self.target_file = Path(target_file)
        self.language = language or self._detect_language()
        self.project_root = self._find_project_root()
        self.functions = []
        self.unused_functions = []
        self.language_config = self._get_language_config()
        
    def _detect_language(self) -> str:
        """Detect programming language from file extension."""
        extension = self.target_file.suffix.lower()
        language_map = {
            '.py': 'python',
            '.gd': 'gdscript',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.cs': 'csharp'
        }
        return language_map.get(extension, 'python')
    
    def _get_language_config(self) -> Dict[str, Any]:
        """Get language-specific configuration."""
        configs = {
            'python': {
                'function_pattern': r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                'file_extensions': ['.py'],
                'builtin_functions': ['__init__', '__str__', '__repr__', '__len__', '__getitem__', '__setitem__'],
                'private_prefix': '_',
                'project_indicators': ['setup.py', 'pyproject.toml', 'requirements.txt', '__init__.py']
            },
            'gdscript': {
                'function_pattern': r'^(\s*)func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:',
                'file_extensions': ['.gd'],
                'builtin_functions': ['_ready', '_process', '_input', '_exit_tree', '_enter_tree'],
                'private_prefix': '_',
                'project_indicators': ['project.godot']
            },
            'javascript': {
                'function_pattern': r'^(\s*)(?:function\s+([a-zA-Z_][a-zA-Z0-9_]*)|(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:function|\([^)]*\)\s*=>))',
                'file_extensions': ['.js'],
                'builtin_functions': [],
                'private_prefix': '_',
                'project_indicators': ['package.json', 'node_modules']
            },
            'typescript': {
                'function_pattern': r'^(\s*)(?:function\s+([a-zA-Z_][a-zA-Z0-9_]*)|(?:const|let|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:function|\([^)]*\)\s*=>)|([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*:\s*[^{]*\s*{)',
                'file_extensions': ['.ts'],
                'builtin_functions': [],
                'private_prefix': '_',
                'project_indicators': ['package.json', 'tsconfig.json', 'node_modules']
            },
            'java': {
                'function_pattern': r'^(\s*)(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                'file_extensions': ['.java'],
                'builtin_functions': ['main', 'toString', 'equals', 'hashCode'],
                'private_prefix': '_',
                'project_indicators': ['pom.xml', 'build.gradle', 'src']
            },
            'cpp': {
                'function_pattern': r'^(\s*)(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:const\s*)?\s*{',
                'file_extensions': ['.cpp', '.c', '.h', '.hpp'],
                'builtin_functions': ['main'],
                'private_prefix': '_',
                'project_indicators': ['CMakeLists.txt', 'Makefile', 'src']
            },
            'csharp': {
                'function_pattern': r'^(\s*)(?:public|private|protected|internal)?\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                'file_extensions': ['.cs'],
                'builtin_functions': ['Main', 'ToString', 'Equals', 'GetHashCode'],
                'private_prefix': '_',
                'project_indicators': ['.csproj', '.sln', 'src']
            }
        }
        return configs.get(self.language, configs['python'])
    
    def _find_project_root(self) -> Path:
        """Find the project root by looking for language-specific indicators"""
        current = self.target_file.parent
        indicators = self.language_config.get('project_indicators', [])
        
        while current != current.parent:
            for indicator in indicators:
                if (current / indicator).exists():
                    return current
            current = current.parent
        
        # If we can't find project indicators, assume we're in the project root
        return Path(".")
    
    def extract_functions(self) -> List[Dict[str, Any]]:
        """Extract all function definitions from the target file"""
        if not self.target_file.exists():
            print(f"❌ File not found: {self.target_file}")
            return []
        
        with open(self.target_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get language-specific function pattern
        func_pattern = self.language_config['function_pattern']
        builtin_functions = self.language_config['builtin_functions']
        private_prefix = self.language_config['private_prefix']
        
        functions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            match = re.match(func_pattern, line)
            if match:
                indent = match.group(1)
                # Handle different regex group structures for different languages
                func_name = None
                for group in match.groups()[1:]:  # Skip the first group (indent)
                    if group:
                        func_name = group
                        break
                
                if not func_name:
                    continue
                
                # Skip private functions unless they're public API
                if func_name.startswith(private_prefix) and not self._is_public_api(func_name):
                    continue
                
                # Skip built-in functions
                if func_name in builtin_functions:
                    continue
                
                functions.append({
                    'name': func_name,
                    'line': i,
                    'indent': len(indent),
                    'is_static': 'static' in line,
                    'is_private': func_name.startswith(private_prefix),
                    'language': self.language
                })
        
        self.functions = functions
        return functions
    
    def _is_public_api(self, func_name: str) -> bool:
        """Check if a private function is actually public API (like signal handlers)"""
        # Signal handlers that might be called externally
        signal_handlers = ['_on_', '_handle_', '_process_', '_update_']
        return any(func_name.startswith(prefix) for prefix in signal_handlers)
    
    def search_function_usage(self, func_name: str) -> List[Dict[str, Any]]:
        """Search for usage of a function across the entire codebase"""
        usage_locations = []
        
        # Search in files with language-specific extensions
        extensions = self.language_config['file_extensions']
        search_files = []
        for ext in extensions:
            search_files.extend(list(self.project_root.rglob(f"*{ext}")))
        
        for file_path in search_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        # Skip the function definition itself
                        if file_path == self.target_file and f"func {func_name}(" in line:
                            continue
                        
                        # Search for function calls
                        if self._is_function_call(line, func_name):
                            usage_locations.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'content': line.strip()
                            })
            except Exception as e:
                print(f"⚠️  Warning: Could not read {file_path}: {e}")
        
        return usage_locations
    
    def _is_function_call(self, line: str, func_name: str) -> bool:
        """Check if a line contains a call to the function"""
        # Remove comments
        line = re.sub(r'#.*$', '', line)
        
        # Pattern for function calls
        patterns = [
            rf'\b{func_name}\s*\(',  # Direct call: function_name(
            rf'\.{func_name}\s*\(',  # Method call: object.function_name(
            rf'{func_name}\.connect', # Signal connection: signal.connect
            rf'connect\s*\(\s*{func_name}', # Signal connection: connect(function_name
        ]
        
        for pattern in patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def audit_functions(self, verbose: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform the complete audit
        
        Args:
            verbose: Whether to print progress information
            
        Returns:
            Dictionary with 'unused' and 'used' function lists
        """
        if verbose:
            print(f"🔍 Auditing functions in: {self.target_file.relative_to(self.project_root)}")
            print(f"📁 Project root: {self.project_root}")
            print()
        
        # Extract functions
        functions = self.extract_functions()
        if not functions:
            if verbose:
                print("❌ No functions found in file")
            return {'unused': [], 'used': []}
        
        if verbose:
            print(f"📋 Found {len(functions)} functions to audit:")
            for func in functions:
                print(f"   - {func['name']} (line {func['line']})")
            print()
        
        # Check usage for each function
        unused = []
        used = []
        
        for func in functions:
            if verbose:
                print(f"🔍 Checking usage of: {func['name']}")
            usage = self.search_function_usage(func['name'])
            
            if usage:
                used.append({
                    'function': func,
                    'usage': usage
                })
                if verbose:
                    print(f"   ✅ Used {len(usage)} times")
                    for use in usage[:3]:  # Show first 3 usages
                        print(f"      - {use['file']}:{use['line']}")
                    if len(usage) > 3:
                        print(f"      ... and {len(usage) - 3} more")
            else:
                unused.append(func)
                if verbose:
                    print(f"   ❌ UNUSED")
        
        if verbose:
            print()
        
        return {'unused': unused, 'used': used}
    
    def generate_report(self, audit_result: Dict[str, List[Dict[str, Any]]], verbose: bool = True):
        """Generate a detailed report"""
        if not verbose:
            return
            
        unused = audit_result['unused']
        used = audit_result['used']
        
        print("=" * 80)
        print("📊 FUNCTION USAGE AUDIT REPORT")
        print("=" * 80)
        print(f"📁 File: {self.target_file.relative_to(self.project_root)}")
        print(f"📋 Total functions: {len(unused) + len(used)}")
        print(f"✅ Used functions: {len(used)}")
        print(f"❌ Unused functions: {len(unused)}")
        print()
        
        if unused:
            print("🚨 UNUSED FUNCTIONS:")
            print("-" * 40)
            for func in unused:
                print(f"   ❌ {func['name']} (line {func['line']})")
            print()
            
            print("💡 RECOMMENDATIONS:")
            print("-" * 40)
            print("   • Review each unused function")
            print("   • Consider if it's planned for future use")
            print("   • Comment out with clear markers if keeping")
            print("   • Delete if truly unnecessary")
            print()
        
        if used:
            print("✅ USED FUNCTIONS:")
            print("-" * 40)
            for item in used:
                func = item['function']
                usage = item['usage']
                print(f"   ✅ {func['name']} (line {func['line']}) - used {len(usage)} times")
            print()


class BatchFunctionAuditor:
    """
    Audits multiple files for unused functions across multiple programming languages.
    
    This class provides batch processing capabilities for auditing entire
    folders or categories of files at once. Supports multiple programming languages.
    """
    
    def __init__(self, project_root: Optional[str] = None, language: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else self._find_project_root()
        self.language = language or 'python'
        self.results = []
        self.language_config = self._get_language_config()
        
    def _get_language_config(self) -> Dict[str, Any]:
        """Get language-specific configuration."""
        configs = {
            'python': {
                'file_extensions': ['.py'],
                'project_indicators': ['setup.py', 'pyproject.toml', 'requirements.txt', '__init__.py']
            },
            'gdscript': {
                'file_extensions': ['.gd'],
                'project_indicators': ['project.godot']
            },
            'javascript': {
                'file_extensions': ['.js'],
                'project_indicators': ['package.json', 'node_modules']
            },
            'typescript': {
                'file_extensions': ['.ts'],
                'project_indicators': ['package.json', 'tsconfig.json', 'node_modules']
            },
            'java': {
                'file_extensions': ['.java'],
                'project_indicators': ['pom.xml', 'build.gradle', 'src']
            },
            'cpp': {
                'file_extensions': ['.cpp', '.c', '.h', '.hpp'],
                'project_indicators': ['CMakeLists.txt', 'Makefile', 'src']
            },
            'csharp': {
                'file_extensions': ['.cs'],
                'project_indicators': ['.csproj', '.sln', 'src']
            }
        }
        return configs.get(self.language, configs['python'])
    
    def _find_project_root(self) -> Path:
        """Find the project root by looking for language-specific indicators"""
        current = Path.cwd()
        indicators = self.language_config.get('project_indicators', [])
        
        while current != current.parent:
            for indicator in indicators:
                if (current / indicator).exists():
                    return current
            current = current.parent
        return Path(".")
    
    def get_files_by_category(self, category: str) -> List[Path]:
        """Get files by category (deprecated - use get_files_in_folder instead)"""
        base_path = self.project_root / "scripts"
        
        if category == "managers":
            return list(base_path.rglob("Managers/**/*.gd"))
        elif category == "ui":
            return list(base_path.rglob("UI/**/*.gd"))
        elif category == "utils":
            return list(base_path.rglob("Utils/**/*.gd"))
        elif category == "factories":
            return list(base_path.rglob("Factories/**/*.gd"))
        elif category == "coordinators":
            return list(base_path.rglob("Coordinators/**/*.gd"))
        else:
            return []
    
    def get_files_by_extension(self, extension: Optional[str] = None, base_folder: str = ".") -> List[Path]:
        """Get all files with specific extension in a base folder"""
        if extension is None:
            # Use language-specific extensions
            extensions = self.language_config['file_extensions']
            files = []
            for ext in extensions:
                files.extend(list(self.project_root.rglob(f"**/*{ext}")))
            return files
        else:
            base_path = self.project_root / base_folder
            if not base_path.exists():
                return []
            return list(base_path.rglob(f"**/*.{extension}"))
    
    def get_files_by_pattern(self, pattern: str, base_folder: str = "scripts") -> List[Path]:
        """Get files matching a glob pattern in a base folder"""
        base_path = self.project_root / base_folder
        if not base_path.exists():
            return []
        return list(base_path.rglob(pattern))
    
    def get_files_in_folder(self, folder_path: str) -> List[Path]:
        """Get all files with language-specific extensions in a specific folder"""
        folder = self.project_root / folder_path
        if not folder.exists():
            print(f"❌ Folder not found: {folder}")
            return []
        
        extensions = self.language_config['file_extensions']
        files = []
        for ext in extensions:
            files.extend(list(folder.rglob(f"*{ext}")))
        return files
    
    def get_all_files(self) -> List[Path]:
        """Get all files with language-specific extensions in the project"""
        extensions = self.language_config['file_extensions']
        files = []
        for ext in extensions:
            files.extend(list(self.project_root.rglob(f"**/*{ext}")))
        return files
    
    def audit_files(self, files: List[Path], show_details: bool = True, 
                   unused_only: bool = False, verbose: bool = True) -> Dict[str, Any]:
        """
        Audit multiple files using the FunctionAuditor class
        
        Args:
            files: List of file paths to audit
            show_details: Whether to show detailed information for each file
            unused_only: Whether to show only files with unused functions
            verbose: Whether to print progress information
            
        Returns:
            Dictionary with audit results
        """
        if verbose:
            print(f"🔍 Starting batch audit of {len(files)} files...")
            print(f"📁 Project root: {self.project_root}")
            print("=" * 80)
        
        results = {
            'files_audited': 0,
            'files_with_unused': 0,
            'total_functions': 0,
            'total_unused': 0,
            'file_results': []
        }
        
        for i, file_path in enumerate(files, 1):
            if verbose:
                print(f"\n[{i}/{len(files)}] Auditing: {file_path.relative_to(self.project_root)}")
            
            try:
                # Use the FunctionAuditor class (DRY principle)
                auditor = FunctionAuditor(str(file_path), language=self.language)
                audit_result = auditor.audit_functions(verbose=False)
                
                file_result = {
                    'file': str(file_path.relative_to(self.project_root)),
                    'unused_count': len(audit_result['unused']),
                    'total_count': len(audit_result['unused']) + len(audit_result['used']),
                    'unused_functions': audit_result['unused'],
                    'used_functions': audit_result['used']
                }
                
                results['file_results'].append(file_result)
                results['files_audited'] += 1
                results['total_functions'] += file_result['total_count']
                results['total_unused'] += file_result['unused_count']
                
                if file_result['unused_count'] > 0:
                    results['files_with_unused'] += 1
                
                # Show details based on options
                if show_details and (not unused_only or file_result['unused_count'] > 0):
                    self._print_file_summary(file_result)
                    if file_result['unused_count'] > 0:
                        print("   🚨 UNUSED FUNCTIONS:")
                        for func in file_result['unused_functions']:
                            print(f"      ❌ {func['name']} (line {func['line']})")
                        print()
                
            except Exception as e:
                if verbose:
                    print(f"   ❌ Error auditing file: {e}")
                continue
        
        return results
    
    def _print_file_summary(self, file_result: Dict[str, Any]):
        """Print summary for a single file"""
        unused = file_result['unused_count']
        total = file_result['total_count']
        status = "❌" if unused > 0 else "✅"
        print(f"   {status} {total} functions, {unused} unused")
    
    def get_unused_functions_list(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get a flat list of all unused functions across all files
        
        Returns:
            List of dictionaries with file, function name, and line number
        """
        unused_functions = []
        for file_result in results['file_results']:
            if file_result['unused_count'] > 0:
                for func in file_result['unused_functions']:
                    unused_functions.append({
                        'file': file_result['file'],
                        'function': func['name'],
                        'line': func['line']
                    })
        return unused_functions
    
    def generate_batch_report(self, results: Dict[str, Any], verbose: bool = True):
        """Generate comprehensive batch report"""
        if not verbose:
            return
            
        print("\n" + "=" * 80)
        print("📊 BATCH FUNCTION USAGE AUDIT REPORT")
        print("=" * 80)
        
        print(f"📁 Project: {self.project_root}")
        print(f"📋 Files audited: {results['files_audited']}")
        print(f"🚨 Files with unused functions: {results['files_with_unused']}")
        print(f"📊 Total functions: {results['total_functions']}")
        print(f"❌ Total unused functions: {results['total_unused']}")
        
        if results['total_functions'] > 0:
            unused_percentage = (results['total_unused'] / results['total_functions']) * 100
            print(f"📈 Unused function percentage: {unused_percentage:.1f}%")
        
        print()
        
        # Files with unused functions
        if results['files_with_unused'] > 0:
            print("🚨 FILES WITH UNUSED FUNCTIONS:")
            print("-" * 50)
            for file_result in results['file_results']:
                if file_result['unused_count'] > 0:
                    print(f"   ❌ {file_result['file']} ({file_result['unused_count']} unused)")
                    # Show the actual unused function names
                    unused_names = [func['name'] for func in file_result['unused_functions']]
                    print(f"      Functions: {', '.join(unused_names)}")
            print()
            
            print("💡 RECOMMENDATIONS:")
            print("-" * 50)
            print("   • Review each file with unused functions")
            print("   • Consider if functions are planned for future use")
            print("   • Comment out with clear markers if keeping")
            print("   • Delete if truly unnecessary")
            print("   • Use the individual audit script for detailed analysis")
            print()
        
        # Clean files
        clean_files = results['files_audited'] - results['files_with_unused']
        if clean_files > 0:
            print(f"✅ CLEAN FILES ({clean_files}):")
            print("-" * 50)
            for file_result in results['file_results']:
                if file_result['unused_count'] == 0:
                    print(f"   ✅ {file_result['file']}")
            print()
    
    def generate_unused_functions_report(self, results: Dict[str, Any], verbose: bool = True):
        """
        Generate a detailed report of all unused functions
        
        Args:
            results: Results from audit_files()
            verbose: Whether to print the report
        """
        unused_functions = self.get_unused_functions_list(results)
        
        if not verbose:
            return unused_functions
            
        print("\n" + "=" * 80)
        print("📋 DETAILED UNUSED FUNCTIONS REPORT")
        print("=" * 80)
        
        if not unused_functions:
            print("🎉 No unused functions found!")
            return unused_functions
        
        print(f"📊 Total unused functions: {len(unused_functions)}")
        print()
        
        # Group by file for better readability
        files_with_unused = {}
        for func in unused_functions:
            file_path = func['file']
            if file_path not in files_with_unused:
                files_with_unused[file_path] = []
            files_with_unused[file_path].append(func)
        
        for file_path, functions in files_with_unused.items():
            print(f"📁 {file_path} ({len(functions)} unused):")
            for func in functions:
                print(f"   ❌ {func['function']} (line {func['line']})")
            print()
        
        return unused_functions


# CLI interface for standalone usage
def main():
    """CLI interface for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Function Usage Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python function_auditor.py file.gd                    # Audit single file
  python function_auditor.py --batch --managers         # Batch audit managers
  python function_auditor.py --batch --all --summary    # Batch audit all files
        """
    )
    
    parser.add_argument('file', nargs='?', help='Single file to audit')
    parser.add_argument('--batch', action='store_true', help='Run batch audit')
    parser.add_argument('--all', action='store_true', help='Audit all files')
    parser.add_argument('--managers', action='store_true', help='Audit manager files')
    parser.add_argument('--ui', action='store_true', help='Audit UI files')
    parser.add_argument('--utils', action='store_true', help='Audit utility files')
    parser.add_argument('--factories', action='store_true', help='Audit factory files')
    parser.add_argument('--coordinators', action='store_true', help='Audit coordinator files')
    parser.add_argument('--folder', type=str, help='Audit files in folder')
    parser.add_argument('--summary', action='store_true', help='Show only summary')
    parser.add_argument('--unused-only', action='store_true', help='Show only unused functions')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch audit
        batch_auditor = BatchFunctionAuditor()
        
        if args.all:
            files = batch_auditor.get_all_files()
        elif args.managers:
            files = batch_auditor.get_files_by_category("managers")
        elif args.ui:
            files = batch_auditor.get_files_by_category("ui")
        elif args.utils:
            files = batch_auditor.get_files_by_category("utils")
        elif args.factories:
            files = batch_auditor.get_files_by_category("factories")
        elif args.coordinators:
            files = batch_auditor.get_files_by_category("coordinators")
        elif args.folder:
            files = batch_auditor.get_files_in_folder(args.folder)
        else:
            print("❌ No batch audit target specified")
            return
        
        if not files:
            print("❌ No files found to audit")
            return
        
        results = batch_auditor.audit_files(
            files,
            show_details=not args.summary,
            unused_only=args.unused_only
        )
        batch_auditor.generate_batch_report(results)
        
    elif args.file:
        # Single file audit
        auditor = FunctionAuditor(args.file)
        result = auditor.audit_functions()
        auditor.generate_report(result)
        
    else:
        print("❌ No file specified. Use --help for options.")
        parser.print_help()

if __name__ == "__main__":
    main()

"""
🔍 Function Auditor Tool

This tool analyzes codebases to identify unused functions and provides cleanup recommendations.
Supports multiple programming languages and provides detailed analysis reports.

Usage:
    Development: python -m scriptcraft.tools.function_auditor.main [args]
    Distributable: python main.py [args]
    Pipeline: Called via main_runner(**kwargs)
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# === Environment Detection & Import Setup ===
# Import the environment detection module
from .env import setup_environment

# Set up environment and get imports
IS_DISTRIBUTABLE = setup_environment()

# Import based on environment
if IS_DISTRIBUTABLE:
    # Distributable imports - use cu pattern for consistency
    import common as cu
else:
    # Development imports - use cu pattern for consistency
    import scriptcraft.common as cu

# Import the core auditor classes
from .function_auditor import FunctionAuditor, BatchFunctionAuditor


class FunctionAuditorTool(cu.BaseTool):
    """Tool for auditing unused functions in codebases."""
    
    def __init__(self) -> None:
        """Initialize the tool."""
        super().__init__(
            name="Function Auditor",
            description="🔍 Audits unused functions in codebases and provides cleanup recommendations",
            tool_name="function_auditor"
        )
        
        # Get tool-specific configuration
        tool_config = self.get_tool_config()
        self.default_language = tool_config.get("default_language", "python")
        self.supported_languages = tool_config.get("supported_languages", [
            "python", "gdscript", "javascript", "typescript", "java", "cpp", "csharp"
        ])
    
    def run(self,
            mode: Optional[str] = None,
            input_paths: Optional[List[Union[str, Path]]] = None,
            output_dir: Optional[Union[str, Path]] = None,
            domain: Optional[str] = None,
            output_filename: Optional[str] = None,
            **kwargs: Any) -> None:
        """
        Run the function auditing process.
        
        Args:
            mode: Auditing mode (e.g., 'single', 'batch', 'folder', 'pattern')
            input_paths: List containing paths to files or directories to audit
            output_dir: Directory to save audit reports
            domain: Optional domain context (not used for function auditing)
            output_filename: Optional custom output filename
            **kwargs: Additional arguments:
                - language: Programming language to analyze (default: auto-detect)
                - extension: File extension to search for (e.g., 'py', 'gd', 'js')
                - pattern: Glob pattern for file matching
                - folder: Specific folder to audit
                - summary_only: Show only summary results
                - unused_only: Show only unused functions
                - detailed_unused: Show detailed unused functions report
        """
        self.log_start()
        
        try:
            # Resolve output directory using DRY method
            output_path = self.resolve_output_directory(output_dir or self.default_output_dir)
            
            # Get auditing parameters
            language = kwargs.get('language', self.default_language)
            extension = kwargs.get('extension', self._get_extension_for_language(language))
            pattern = kwargs.get('pattern')
            folder = kwargs.get('folder')
            summary_only = kwargs.get('summary_only', False)
            unused_only = kwargs.get('unused_only', False)
            detailed_unused = kwargs.get('detailed_unused', False)
            
            # Determine mode and execute accordingly
            if mode == 'single' or (input_paths and len(input_paths) == 1):
                self._process_single_file_mode(input_paths[0], output_path, language, **kwargs)
            elif mode == 'batch' or mode == 'folder' or mode == 'pattern' or (input_paths and len(input_paths) > 1):
                self._process_batch_mode(
                    input_paths, output_path, language, extension, pattern, folder,
                    summary_only, unused_only, detailed_unused, **kwargs
                )
            else:
                # Default to batch mode with current directory
                cu.log_and_print("🔍 No specific mode specified, running batch audit on current directory")
                self._process_batch_mode(
                    None, output_path, language, extension, pattern, folder,
                    summary_only, unused_only, detailed_unused, **kwargs
                )
            
            self.log_completion(output_path)
            
        except Exception as e:
            self.log_error(f"Function audit failed: {e}")
            raise
    
    def _process_single_file_mode(self, file_path: Union[str, Path], output_path: Path, 
                                 language: str, **kwargs: Any) -> None:
        """Process single file auditing mode."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"❌ File not found: {file_path}")
        
        cu.log_and_print(f"🔍 Auditing single file: {file_path}")
        
        # Create auditor and run analysis
        auditor = FunctionAuditor(str(file_path))
        result = auditor.audit_functions(verbose=True)
        
        # Generate report
        auditor.generate_report(result, verbose=True)
        
        # Save results to file
        self._save_audit_results(result, output_path, f"{file_path.stem}_audit")
    
    def _process_batch_mode(self, input_paths: Optional[List[Union[str, Path]]], 
                           output_path: Path, language: str, extension: str,
                           pattern: Optional[str], folder: Optional[str],
                           summary_only: bool, unused_only: bool, detailed_unused: bool,
                           **kwargs: Any) -> None:
        """Process batch auditing mode."""
        cu.log_and_print(f"🔍 Starting batch audit (language: {language}, extension: {extension})")
        
        # Create batch auditor
        batch_auditor = BatchFunctionAuditor()
        
        # Determine files to audit
        if input_paths:
            # Use provided input paths
            files = [Path(p) for p in input_paths if Path(p).exists()]
            if not files:
                raise ValueError("❌ No valid input files found")
        elif pattern:
            # Use pattern matching
            files = batch_auditor.get_files_by_pattern(pattern, ".")
            cu.log_and_print(f"📁 Found {len(files)} files matching pattern: {pattern}")
        elif folder:
            # Use specific folder
            files = batch_auditor.get_files_in_folder(folder)
            cu.log_and_print(f"📁 Found {len(files)} files in folder: {folder}")
        else:
            # Use extension-based search
            files = batch_auditor.get_files_by_extension(extension, ".")
            cu.log_and_print(f"📁 Found {len(files)} files with extension: {extension}")
        
        if not files:
            cu.log_and_print("❌ No files found to audit")
            return
        
        # Run batch audit
        results = batch_auditor.audit_files(
            files,
            show_details=not summary_only,
            unused_only=unused_only,
            verbose=True
        )
        
        # Generate reports
        batch_auditor.generate_batch_report(results, verbose=True)
        
        if detailed_unused:
            batch_auditor.generate_unused_functions_report(results, verbose=True)
        
        # Save results to file
        self._save_batch_results(results, output_path, language)
    
    def _save_audit_results(self, result: Dict[str, Any], output_path: Path, filename: str) -> None:
        """Save single file audit results."""
        import json
        
        # Create summary
        summary = {
            'total_functions': len(result['unused']) + len(result['used']),
            'used_functions': len(result['used']),
            'unused_functions': len(result['unused']),
            'unused_percentage': (len(result['unused']) / (len(result['unused']) + len(result['used']))) * 100 if (len(result['unused']) + len(result['used'])) > 0 else 0
        }
        
        # Save summary
        summary_file = output_path / f"{filename}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed results
        results_file = output_path / f"{filename}_detailed.json"
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        cu.log_and_print(f"📊 Results saved to: {summary_file} and {results_file}")
    
    def _save_batch_results(self, results: Dict[str, Any], output_path: Path, language: str) -> None:
        """Save batch audit results."""
        import json
        
        # Save batch results
        results_file = output_path / f"batch_audit_{language}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        cu.log_and_print(f"📊 Batch results saved to: {results_file}")
    
    def _get_extension_for_language(self, language: str) -> str:
        """Get file extension for a programming language."""
        extensions = {
            'python': 'py',
            'gdscript': 'gd',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'cpp': 'cpp',
            'csharp': 'cs'
        }
        return extensions.get(language.lower(), 'py')


def main():
    """Main entry point for the function auditor tool."""
    args = cu.parse_tool_args("🔍 Audits unused functions in codebases and provides cleanup recommendations")
    
    # Create and run the tool
    tool = FunctionAuditorTool()
    tool.run(
        input_paths=args.input_paths,
        output_dir=args.output_dir,
        domain=args.domain,
        output_filename=args.output_filename,
        mode=args.mode
    )


if __name__ == "__main__":
    main()

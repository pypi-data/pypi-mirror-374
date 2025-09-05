#!/usr/bin/env python3
"""
CLI wrapper for the ScriptCraft Function Auditor Plugin
This provides a simple command-line interface to the function auditing capabilities.

Usage:
    python audit_functions_cli.py <file_path>                    # Audit single file
    python audit_functions_cli.py --batch --managers             # Batch audit managers
    python audit_functions_cli.py --batch --all --summary        # Batch audit all files
"""

import sys
from pathlib import Path

# Add the scriptcraft_plugins directory to the path
sys.path.insert(0, str(Path(__file__).parent / "scriptcraft_plugins"))

from function_auditor import FunctionAuditor, BatchFunctionAuditor

def main():
    """CLI interface using the ScriptCraft plugin"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Function Usage Audit Tool (ScriptCraft Plugin)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit_functions_cli.py file.gd                           # Audit single file
  python audit_functions_cli.py --batch --all                     # Audit all .gd files
  python audit_functions_cli.py --batch --folder scripts/Managers # Audit specific folder
  python audit_functions_cli.py --batch --pattern "**/*Manager*"  # Audit files matching pattern
  python audit_functions_cli.py --batch --extension py --base-folder src  # Audit Python files
  python audit_functions_cli.py --batch --all --detailed-unused   # Show detailed unused functions
        """
    )
    
    parser.add_argument('file', nargs='?', help='Single file to audit')
    parser.add_argument('--batch', action='store_true', help='Run batch audit')
    parser.add_argument('--all', action='store_true', help='Audit all files')
    parser.add_argument('--managers', action='store_true', help='Audit manager files (deprecated - use --folder)')
    parser.add_argument('--ui', action='store_true', help='Audit UI files (deprecated - use --folder)')
    parser.add_argument('--utils', action='store_true', help='Audit utility files (deprecated - use --folder)')
    parser.add_argument('--factories', action='store_true', help='Audit factory files (deprecated - use --folder)')
    parser.add_argument('--coordinators', action='store_true', help='Audit coordinator files (deprecated - use --folder)')
    parser.add_argument('--folder', type=str, help='Audit files in specific folder (e.g., "scripts/Managers")')
    parser.add_argument('--extension', type=str, default='gd', help='File extension to audit (default: gd)')
    parser.add_argument('--pattern', type=str, help='Glob pattern to match files (e.g., "**/*Manager*.gd")')
    parser.add_argument('--base-folder', type=str, default='scripts', help='Base folder to search in (default: scripts)')
    parser.add_argument('--summary', action='store_true', help='Show only summary')
    parser.add_argument('--unused-only', action='store_true', help='Show only unused functions')
    parser.add_argument('--detailed-unused', action='store_true', help='Show detailed unused functions report')
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch audit using the plugin
            batch_auditor = BatchFunctionAuditor()
            
            if args.all:
                files = batch_auditor.get_all_files()
            elif args.pattern:
                # Use pattern matching
                files = batch_auditor.get_files_by_pattern(args.pattern, args.base_folder)
            elif args.folder:
                # Use specific folder
                files = batch_auditor.get_files_in_folder(args.folder)
            elif args.extension != 'gd' or args.base_folder != 'scripts':
                # Use extension/base folder combination
                files = batch_auditor.get_files_by_extension(args.extension, args.base_folder)
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
            else:
                print("❌ No batch audit target specified")
                print("💡 Use --folder, --pattern, --extension, or --all")
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
            
            # Show detailed unused functions report if requested
            if args.detailed_unused:
                batch_auditor.generate_unused_functions_report(results)
            
        elif args.file:
            # Single file audit using the plugin
            auditor = FunctionAuditor(args.file)
            result = auditor.audit_functions()
            auditor.generate_report(result)
            
        else:
            print("❌ No file specified. Use --help for options.")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⏹️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during audit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
🔍 Function Auditor Tool

A comprehensive tool for auditing unused functions in codebases.
Supports multiple programming languages and provides detailed analysis reports.

Features:
- 🔍 Function usage analysis
- 📊 Batch processing capabilities
- 🎯 Smart function detection
- 📋 Comprehensive reporting
- 🔄 Multi-language support
- ⚠️ Unused function identification
- 🧹 Code cleanup recommendations

Author: ScriptCraft Team
"""

# === WILDCARD IMPORTS FOR SCALABILITY ===
from .main import *
from .function_auditor import *

# === FUTURE API CONTROL (COMMENTED) ===
# Uncomment and populate when you want to control public API
# __all__ = [
#     'FunctionAuditorTool',
#     'FunctionAuditor',
#     'BatchFunctionAuditor'
# ]

# Tool metadata
__description__ = "🔍 Audits unused functions in codebases and provides cleanup recommendations"
__tags__ = ["code-analysis", "refactoring", "cleanup", "functions", "unused-code", "code-quality"]
__data_types__ = ["python", "gdscript", "javascript", "typescript", "java", "cpp", "csharp"]
__domains__ = ["development", "code-quality", "refactoring", "maintenance"]
__complexity__ = "moderate"
__maturity__ = "stable"
__distribution__ = "standalone"

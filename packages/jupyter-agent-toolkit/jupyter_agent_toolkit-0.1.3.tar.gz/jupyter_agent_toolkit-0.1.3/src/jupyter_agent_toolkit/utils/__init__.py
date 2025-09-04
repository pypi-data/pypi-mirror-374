"""
Utilities for simplified jupyter-agent-toolkit usage.

This module provides high-level convenience functions for common patterns
when working with kernels, notebooks, and execution workflows.
"""

from .factories import create_kernel, create_notebook_transport
from .outputs import extract_outputs, format_output, get_result_value
from .execution import (
    execute_code,
    invoke_code_cell,
    invoke_existing_cell,
    invoke_markdown_cell, 
    invoke_notebook_cells,
    convert_to_notebook_result,
    get_session_info,
    get_variables,
    get_variable_value,
)
from .packages import (
    ensure_packages,
    update_dependencies,
    install_package,
    check_package_availability,
    SCIENTIFIC_PACKAGES,
    ML_PACKAGES,
    DATA_VIZ_PACKAGES,
    WEB_PACKAGES,
)
# Import notebook utilities from notebook module to avoid circular imports
from ..notebook.utils import (
    create_minimal_notebook_content,
    create_notebook_via_contents_api,
)

__all__ = [
    "create_kernel",
    "create_notebook_transport", 
    "extract_outputs",
    "format_output",
    "get_result_value",
    "execute_code",
    "invoke_code_cell",
    "invoke_existing_cell",
    "invoke_markdown_cell",
    "invoke_notebook_cells",
    "convert_to_notebook_result",
    "get_session_info",
    "get_variables", 
    "get_variable_value",
    "ensure_packages",
    "update_dependencies",
    "install_package", 
    "check_package_availability",
    "SCIENTIFIC_PACKAGES",
    "ML_PACKAGES",
    "DATA_VIZ_PACKAGES", 
    "WEB_PACKAGES",
    "create_minimal_notebook_content",
    "create_notebook_via_contents_api"
]
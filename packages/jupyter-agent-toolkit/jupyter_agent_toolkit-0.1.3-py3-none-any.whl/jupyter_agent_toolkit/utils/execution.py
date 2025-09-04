"""
High-level execution utilities for AI agents.

This module provides simplified functions for executing code and managing
notebook workflows with sensible defaults and error handling.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Union

from ..kernel.types import ExecutionResult, NotebookExecutionResult
from ..notebook.session import NotebookSession
from ..notebook.utils import to_nbformat_outputs
from .outputs import extract_outputs, format_output, has_error

logger = logging.getLogger(__name__)


def convert_to_notebook_result(
    result: ExecutionResult,
    cell_index: int,
    *,
    elapsed_seconds: Optional[float] = None,
    format_outputs: bool = True
) -> NotebookExecutionResult:
    """
    Create a NotebookExecutionResult from a basic ExecutionResult.
    
    Args:
        result: Basic ExecutionResult from kernel execution
        cell_index: Index of the executed cell
        elapsed_seconds: Execution time
        format_outputs: Whether to process outputs for readability
        
    Returns:
        NotebookExecutionResult with enhanced fields
    """
    outputs = to_nbformat_outputs(result) or []
    
    formatted_output = format_output(outputs) if format_outputs else ""
    error_message = None
    
    # Extract error message if execution failed
    if has_error(outputs):
        error_outputs = [out for out in outputs if out.get("output_type") == "error"]
        if error_outputs:
            error_message = format_output(error_outputs)
    
    # Use utils extract_outputs for consistent text outputs
    text_outputs = extract_outputs(outputs)
    
    return NotebookExecutionResult(
        status=result.status,
        execution_count=result.execution_count,
        cell_index=cell_index,
        stdout=result.stdout,
        stderr=result.stderr,
        outputs=outputs,
        text_outputs=text_outputs,
        formatted_output=formatted_output,
        error_message=error_message,
        elapsed_seconds=elapsed_seconds
    )


async def execute_code(
    kernel_session,
    code: str,
    *,
    timeout: Optional[float] = 30.0,
    format_outputs: bool = True
) -> NotebookExecutionResult:
    """
    Execute code in a kernel session with automatic output processing.
    
    Note: Returns NotebookExecutionResult for consistency, with cell_index = -1 
    to indicate this was direct kernel execution (not in a notebook).
    
    Args:
        kernel_session: Kernel session to execute in
        code: Python code to execute
        timeout: Execution timeout in seconds
        format_outputs: Whether to format outputs into readable strings
        
    Returns:
        NotebookExecutionResult with processed outputs and metadata
        
    Examples:
        kernel = create_kernel("local")
        result = await execute_code(kernel, "2 + 3")
        
        if result.status == "ok":
            print(f"Result: {result.formatted_output}")
        else:
            print(f"Error: {result.error_message}")
    """
    start_time = time.time()
    
    logger.debug(f"Executing code: {code[:100]}{'...' if len(code) > 100 else ''}")
    
    try:
        # Only start if not already alive
        if not await kernel_session.is_alive():
            await kernel_session.start()
        
        logger.debug("Executing code in kernel session")
        
        if timeout:
            result = await asyncio.wait_for(
                kernel_session.execute(code), 
                timeout=timeout
            )
        else:
            result = await kernel_session.execute(code)
        
        elapsed = time.time() - start_time
        logger.debug(f"Code execution completed in {elapsed:.2f}s, status: {result.status}")
        logger.debug(f"Result type: {type(result)}, outputs: {len(result.outputs) if hasattr(result, 'outputs') else 'No outputs attr'}")
        
        # Convert to NotebookExecutionResult with cell_index = -1 for direct execution
        return convert_to_notebook_result(
            result,
            cell_index=-1,
            elapsed_seconds=elapsed,
            format_outputs=format_outputs
        )
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=-1,
            stdout="",
            stderr="",
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"Execution timed out after {timeout}s",
            elapsed_seconds=elapsed
        )
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Code execution failed: {type(e).__name__}: {e}")
        logger.error(f"Error occurred during: {code[:100]}...")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=-1,
            stdout="",
            stderr=str(e),
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"{type(e).__name__}: {e}",
            elapsed_seconds=elapsed
        )


async def invoke_code_cell(
    notebook_session: NotebookSession,
    code: str,
    *,
    timeout: Optional[float] = 60.0,
    format_outputs: bool = True
) -> NotebookExecutionResult:
    """
    Invoke Python code in a new notebook cell - agent-friendly execution.
    
    Args:
        notebook_session: NotebookSession to execute in
        code: Python code to execute
        timeout: Execution timeout in seconds  
        format_outputs: Whether to format outputs into readable strings
        
    Returns:
        NotebookExecutionResult with cell index and processed outputs
        
    Examples:
        kernel = create_kernel("remote", base_url="http://localhost:8888")
        doc = create_notebook_transport("remote", "analysis.ipynb", 
                                      base_url="http://localhost:8888")
        nb = NotebookSession(kernel=kernel, doc=doc)
        
        result = await invoke_code_cell(nb, "import pandas as pd")
        print(f"Cell {result.cell_index}: {result.formatted_output}")
    """
    start_time = time.time()
    
    try:
        cell_index, result = await notebook_session.append_and_run(code, timeout=timeout)
        
        elapsed = time.time() - start_time
        
        return convert_to_notebook_result(
            result,
            cell_index=cell_index,
            elapsed_seconds=elapsed,
            format_outputs=format_outputs
        )
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=-1,
            stdout="",
            stderr="",
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"Execution timed out after {timeout}s",
            elapsed_seconds=elapsed
        )
        
    except Exception as e:
        elapsed = time.time() - start_time
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=-1,
            stdout="",
            stderr="",
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"{type(e).__name__}: {e}",
            elapsed_seconds=elapsed
        )


async def invoke_markdown_cell(
    notebook_session: NotebookSession,
    markdown: str
) -> int:
    """
    Invoke markdown content in a new notebook cell - agent-friendly documentation.
    
    Args:
        notebook_session: NotebookSession to add cell to
        markdown: Markdown content to add
        
    Returns:
        int: Index of the added cell
        
    Examples:
        cell_index = await invoke_markdown_cell(nb, "## Analysis Results")
        print(f"Added markdown at cell {cell_index}")
    """
    return await notebook_session.run_markdown(markdown)


async def invoke_notebook_cells(
    notebook_session: NotebookSession,
    cells: List[Dict[str, str]],
    *,
    timeout: Optional[float] = 30.0,
    format_outputs: bool = True
) -> List[Union[NotebookExecutionResult, int]]:
    """
    Invoke multiple cells (code and/or markdown) in sequence - agent workflow execution.
    
    Args:
        notebook_session: NotebookSession to execute in
        cells: List of cell dictionaries with 'type' and 'content' keys
                Expected format: [{"type": "code|markdown", "content": "..."}]
        timeout: Execution timeout for code cells
        format_outputs: Whether to format outputs for code cells
        
    Returns:
        List of results - NotebookExecutionResult for code cells, int for markdown cells
        
    Examples:
        cells = [
            {"type": "markdown", "content": "# My Analysis"},
            {"type": "code", "content": "import pandas as pd"},
            {"type": "code", "content": "df = pd.DataFrame({'a': [1,2,3]})"}
        ]
        
        results = await invoke_notebook_cells(nb, cells)
        for i, result in enumerate(results):
            if isinstance(result, NotebookExecutionResult):
                print(f"Cell {i}: Code executed at index {result.cell_index}")
            else:
                print(f"Cell {i}: Markdown added at index {result}")
    """
    results = []
    for cell in cells:
        cell_type = cell.get("type", "code")
        content = cell.get("content", "")
        
        if not content:
            raise ValueError(f"Empty content in cell: {cell}")
        
        if cell_type == "markdown":
            result = await invoke_markdown_cell(notebook_session, content)
        elif cell_type == "code":
            result = await invoke_code_cell(
                notebook_session, content, timeout=timeout, format_outputs=format_outputs
            )
        else:
            raise ValueError(f"Unsupported cell_type: {cell_type}. Must be 'code' or 'markdown'")
        
        results.append(result)
    
    return results


# Session information and variable utilities
async def get_session_info(session) -> Dict[str, any]:
    """
    Get basic information about a kernel session.
    
    Args:
        session: Kernel session object
        
    Returns:
        Dictionary with session information
        
    Examples:
        info = await get_session_info(kernel)
        print(f"Kernel alive: {info['alive']}")
        print(f"Connection: {info['connection_info']}")
    """
    info = {
        "type": type(session).__name__,
        "alive": await session.is_alive(),
        "connection_info": "N/A"
    }
    
    # Add kernel manager info if available (local sessions)
    if hasattr(session, 'kernel_manager') and session.kernel_manager:
        km = session.kernel_manager
        info["connection_info"] = getattr(km, 'connection_file', 'Local kernel')
        info["kernel_name"] = getattr(km, 'kernel_name', 'Unknown')
    
    return info


async def get_variables(session) -> List[str]:
    """
    Get list of variables in the kernel session.
    
    Args:
        session: Kernel session object
        
    Returns:
        List of variable names
        
    Examples:
        vars = await get_variables(kernel)
        print(f"Variables: {vars}")
    """
    from ..kernel.variables import VariableManager
    
    try:
        var_manager = VariableManager(session)
        return await var_manager.list()
    except Exception as e:
        logger.warning(f"Could not list variables: {e}")
        return []


async def get_variable_value(session, name: str) -> any:
    """
    Get the value of a specific variable from the kernel session.
    
    Args:
        session: Kernel session object
        name: Variable name to retrieve
        
    Returns:
        Variable value or None if not found
        
    Examples:
        value = await get_variable_value(kernel, "my_data")
        print(f"my_data = {value}")
    """
    from ..kernel.variables import VariableManager
    
    try:
        var_manager = VariableManager(session)
        return await var_manager.get(name)
    except Exception as e:
        logger.warning(f"Could not get variable '{name}': {e}")
        return None


async def invoke_existing_cell(
    notebook_session: NotebookSession,
    cell_index: int,
    code: str,
    *,
    timeout: Optional[float] = 30.0,
    format_outputs: bool = True
) -> NotebookExecutionResult:
    """
    Invoke code in an existing cell at the specified index - agent cell updates.
    
    This function replaces the source of an existing cell and executes it,
    which is different from invoke_code_cell() that creates a new cell.
    
    Args:
        notebook_session: NotebookSession to execute in
        cell_index: Index of the existing cell to execute (0-based)
        code: Python code to replace the cell source and execute
        timeout: Execution timeout in seconds  
        format_outputs: Whether to format outputs into readable strings
        
    Returns:
        NotebookExecutionResult with cell index and processed outputs
        
    Examples:
        # Execute code in existing cell 2
        result = await invoke_existing_cell(nb, 2, "print('Updated cell!')")
        print(f"Cell {result.cell_index}: {result.formatted_output}")
        
        # vs creating a new cell:
        # result = await invoke_code_cell(nb, "print('New cell!')")
    """
    start_time = time.time()
    
    try:
        await notebook_session.start()
        
        if timeout:
            result = await asyncio.wait_for(
                notebook_session.run_at(cell_index, code),
                timeout=timeout
            )
        else:
            result = await notebook_session.run_at(cell_index, code)
        
        elapsed = time.time() - start_time
        
        return convert_to_notebook_result(
            result,
            cell_index=cell_index,
            elapsed_seconds=elapsed,
            format_outputs=format_outputs
        )
        
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=cell_index,
            stdout="",
            stderr="",
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"Execution timed out after {timeout}s",
            elapsed_seconds=elapsed
        )
        
    except Exception as e:
        elapsed = time.time() - start_time
        return NotebookExecutionResult(
            status="error",
            execution_count=None,
            cell_index=cell_index,
            stdout="",
            stderr="",
            outputs=[],
            text_outputs=[],
            formatted_output="",
            error_message=f"{type(e).__name__}: {e}",
            elapsed_seconds=elapsed
        )

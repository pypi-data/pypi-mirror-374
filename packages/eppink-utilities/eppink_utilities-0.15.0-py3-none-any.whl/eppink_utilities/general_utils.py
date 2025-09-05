import numpy as np
import ast
import os
import ctypes

def sleepmode_prevent():
    """
    Prevents Windows from entering sleep mode or turning off the display.

    This function uses the Windows API to set the execution state of the current thread,
    indicating that the system and display are required. It should be called at the 
    beginning of a long-running process to keep the system awake.

    WARNING:
        You should ensure that `restore_sleep_mode()` is called when the task is finished 
        to return the system to normal power-saving behavior. You can do this manually, 
        or use `atexit.register(restore_sleep_mode)` to restore sleep mode automatically 
        when the program exits.
    """
    ES_CONTINUOUS       = 0x80000000
    ES_SYSTEM_REQUIRED  = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )

def sleepmode_restore():
    """
    Restores the system's normal sleep and display timeout behavior.

    This function clears the execution state flags set by `prevent_sleep_mode()`.
    Call this when your task is complete to allow the system to sleep again.
    """
    ES_CONTINUOUS = 0x80000000
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

def validate_inputs(*args, dtype=float, allow_scalar=True, allow_array=True, check_broadcast=True, scalars_to_arrays=False):
    """
    Validates and converts inputs to NumPy arrays of the specified dtype,
    ensuring that np.nan values are preserved if dtype supports them.

    Parameters:
        *args: Variable length argument list of inputs to be validated and converted.
        dtype: Desired data type of the output arrays (default: float).
        allow_scalar (bool): If False, scalar inputs will raise a ValueError.
        allow_array (bool): If False, array inputs (ndim > 0) will raise a ValueError.
        check_broadcast (bool): If True, checks that all inputs can be broadcast together.

    Returns:
        Each validated input as a separate NumPy array (not packed in a tuple).

    Raises:
        TypeError: If any input cannot be converted to the specified dtype.
        ValueError: If scalar or array inputs are disallowed but found,
                    if inputs cannot be broadcast together,
                    or if nan values are present but dtype is integer.
    """

    arrays = []
    for arg in args:
        arr_raw = np.asarray(arg)  # no dtype yet, preserves nans

        if np.any(np.isnan(arr_raw)):
            if np.issubdtype(dtype, np.integer):
                raise ValueError(f"Input {arg} contains NaN but dtype={dtype} does not support NaN.")

        try:
            arr = np.asarray(arg, dtype=dtype)
        except Exception as e:
            raise TypeError(f"Input {arg} cannot be converted to array of type {dtype}") from e

        if not allow_scalar and arr.ndim == 0:
            raise ValueError(f"Scalar input {arg} not allowed.")

        if not allow_array and arr.ndim > 0:
            raise ValueError(f"Array input {arg} not allowed.")

        arrays.append(arr)

    if check_broadcast:
        try:
            np.broadcast(*arrays)
        except ValueError as e:
            raise ValueError("Inputs are not broadcast-compatible.") from e
        
        if scalars_to_arrays and len(arrays) > 1:
            # Find reference shape: largest shape by total size, ignoring empty tuple
            ref_shape = None
            max_size = 0
            for arr in arrays:
                size = np.prod(arr.shape)
                if size > max_size:
                    max_size = size
                    ref_shape = arr.shape

            # If all inputs are scalars (size=1), ref_shape might be ():
            # So fallback to (1,) shape to allow broadcasting of scalars
            if ref_shape == ():
                ref_shape = (1,)

            # Broadcast scalars and (1,) arrays to the reference shape
            arrays = tuple(
                np.broadcast_to(arr, ref_shape)
                if arr.ndim == 0 or arr.shape == (1,)
                else arr
                for arr in arrays
            )



    return (*arrays,)

def extract_functions_with_docstrings(file_path):
    """
    Parses a Python file and extracts all top-level function names and their docstrings.

    Parameters:
        file_path (str): Path to the Python source file.

    Returns:
        list of tuple: A list of (function_name, docstring) tuples.
                       If a function has no docstring, a placeholder message is used.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)
    functions = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name
            docstring = ast.get_docstring(node)
            functions.append((func_name, docstring or "No description provided."))

    return functions

def list_py_files(directory: str) -> list:
    """
    List all Python files in a directory, excluding '__init__.py'.

    Parameters:
        directory (str): Path to the directory to scan.

    Returns:
        list of str: List of .py file paths.
    """
    py_files = []
    for file in os.listdir(directory):
        if file.endswith(".py") and file != "__init__.py":
            py_files.append(os.path.join(directory, file))
    return py_files
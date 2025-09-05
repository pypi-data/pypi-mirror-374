import numpy as np
from .math_utils import average

def data_row_exists(contents, new_row, column=0):
    """
    Check if the specified column of `new_row` matches the same column of any row in `contents`.

    Parameters:
        new_row (list): A list representing the row to check.
        contents (list of lists): The existing rows to search within, where each row is a list.
        column (int, optional): The index of the column to compare. Defaults to 0.

    Returns:
        tuple: (exists, index, matched_row)
            exists (bool): True if a matching value is found in the specified column, else False.
            index (int or None): The index of the matching row in `contents` if found, else None.
            matched_row (list or None): The matched row from `contents` if found, else None.

    Notes:
        - Matching is based on the value in the specified column.
        - Assumes `new_row` and each row in `contents` have enough columns to access the specified index.
        - Raises IndexError if `column` is out of range for any row.
    """
    key = new_row[column]
    for i, row in enumerate(contents):
        if row and row[column] == key:
            return True, i, row
    return False, None, None

def data_exact_row_exists(contents, new_row, case_sensitive=False, type_sensitive=False):
    """
    Check if a fully identical row exists in `contents`, with options for case and type sensitivity.

    Parameters:
        new_row (list): A list representing the row to check.
        contents (list of lists): The existing rows to search within, where each row is a list.
        case_sensitive (bool, optional): If True, string comparisons are case-sensitive. Defaults to False.
        type_sensitive (bool, optional): If True, type mismatches cause non-match. Defaults to False.

    Returns:
        tuple: (exists, matched_indices)
            exists (bool): True if one or more matches are found based on the given sensitivity options.
            matched_indices (list): A list of indices in `contents` where rows match `new_row` based on sensitivity.

    Notes:
        - Matching requires the same number of elements in each row.
        - If `case_sensitive` is False, string comparisons are case-insensitive.
        - If `type_sensitive` is False, values with equal string representations are considered equal.
    """


    matched_indices = [i for i, row in enumerate(contents) if data_rows_match(row, new_row, case_sensitive==case_sensitive, type_sensitive=type_sensitive)]
    exists = len(matched_indices) > 0
    return exists, matched_indices

def data_rows_match(row1, row2, case_sensitive=False, type_sensitive=False):
    """
    Compares two rows (lists, tuples, etc.) element-wise to determine if they match.

    Parameters:
        row1 (iterable): The first row to compare.
        row2 (iterable): The second row to compare.
        case_sensitive (bool): If True, string comparisons are case-sensitive.
                               If False (default), strings are compared case-insensitively.
        type_sensitive (bool): If True, values are compared with type sensitivity (e.g., 1 != "1").
                               If False (default), values are converted to strings before comparison.

    Returns:
        bool: True if the rows match element-wise according to the specified sensitivity flags,
              False otherwise.
    """
    if len(row1) != len(row2):
        return False
    for v1, v2 in zip(row1, row2):
        if type_sensitive:
            if v1 != v2:
                return False
        else:
            s1, s2 = str(v1), str(v2)
            if case_sensitive:
                if s1 != s2:
                    return False
            else:
                if s1.lower() != s2.lower():
                    return False
    return True

def data_remove_rows(contents, selector, mode="remove", selection_type="indices", column=None, header=True):
    """
    Remove or keep rows from contents based on indices or value range.

    Parameters:
        contents (list of lists): The CSV data as a list of rows (including header if present).
        selector (list of int or tuple of (min,) or (min, max)): Indices or value range depending on selection_type.
        mode (str): "remove" (default) or "keep".
        selection_type (str): "indices" (default) or "range".
        column (int): Column index to use when selection_type is "range".
        header (bool): Whether the first row is a header row to preserve (default True).

    Returns:
        list: Modified list with rows removed or kept based on the given criteria.

    Notes:
        - Invalid indices are ignored in "indices" mode.
        - Range comparisons use float conversion.
        - Header row (row 0) is preserved by default if header=True.
    """
    if selection_type == "indices":
        indices_set = set(selector)
        if mode == "remove":
            return [row for i, row in enumerate(contents) if (header and i == 0) or i not in indices_set]
        elif mode == "keep":
            return [row for i, row in enumerate(contents) if (header and i == 0) or i in indices_set]
        else:
            raise ValueError("Mode must be 'remove' or 'keep'")

    elif selection_type == "range":
        if column is None:
            raise ValueError("Column index must be specified for range-based selection.")
        if not isinstance(selector, (tuple, list)) or len(selector) not in (1, 2):
            raise ValueError("Selector must be a (min,) or (min, max) tuple for range-based selection.")

        # Normalize selector to (min, max)
        if len(selector) == 1:
            min_val, max_val = selector[0], float('inf')
        else:
            min_val, max_val = selector

        def is_in_range(row):
            try:
                val = float(row[column])
                return min_val <= val <= max_val
            except (ValueError, IndexError, TypeError):
                return False  # Skip invalid/missing values

        if mode == "remove":
            return [row for i, row in enumerate(contents) if (header and i == 0) or not is_in_range(row)]
        elif mode == "keep":
            return [row for i, row in enumerate(contents) if (header and i == 0) or is_in_range(row)]
        else:
            raise ValueError("Mode must be 'remove' or 'keep'")

    else:
        raise ValueError("Selection_type must be 'indices' or 'range'")


def data_remove_columns(contents, columns, mode='remove', inputmode='index'):
    """
    Remove or keep specified columns from CSV-like data (list of lists).

    Parameters:
        contents (list of lists): CSV data, first row is header if inputmode='header'.
        columns (list): List of column indices (int) or header names (str).
        mode (str): 'remove' to drop listed columns, 'keep' to keep only listed columns.
        inputmode (str): 'index' if columns are indices, 'header' if columns are header names.

    Returns:
        list of lists: New contents with columns removed or kept accordingly.

    Raises:
        ValueError: If invalid mode, inputmode, duplicates, or invalid column names/indices.
    """

    if mode not in ('remove', 'keep'):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'remove' or 'keep'.")
    if inputmode not in ('index', 'header'):
        raise ValueError(f"Invalid inputmode '{inputmode}'. Must be 'index' or 'header'.")

    if not contents or not contents[0]:
        # No data or no header row to work with
        return []

    header = contents[0]
    n_cols = len(header)

    # Remove duplicates and keep order
    def unique(seq):
        seen = set()
        return [x for x in seq if not (x in seen or seen.add(x))]

    columns = unique(columns)
    if len(columns) < 1:
        # Nothing specified, just return all columns as-is
        return contents.copy()

    if inputmode == 'header':
        # Validate header exists
        if not isinstance(header, list):
            raise ValueError("First row must be a list of header names.")

        # Map headers to indices
        try:
            col_indices = [header.index(col) for col in columns]
        except ValueError as e:
            raise ValueError(f"Column name not found: {e}")

    else:
        # inputmode == 'index'
        # Validate all indices are ints and in range
        if not all(isinstance(c, int) for c in columns):
            raise ValueError("All columns must be integers when inputmode='index'.")
        if any(c < 0 or c >= n_cols for c in columns):
            raise ValueError(f"Column index out of range. Allowed 0 to {n_cols-1}.")
        col_indices = columns

    col_indices_set = set(col_indices)

    if mode == 'remove':
        # Keep all columns NOT in col_indices
        cols_to_keep = [i for i in range(n_cols) if i not in col_indices_set]
    else:
        # mode == 'keep'
        cols_to_keep = col_indices

    # Build new contents with selected columns
    new_contents = []
    for row in contents:
        # Defensive: skip rows with unexpected length
        if len(row) < n_cols:
            raise ValueError("Row length shorter than header length.")
        new_row = [row[i] for i in cols_to_keep]
        new_contents.append(new_row)

    return new_contents

def data_columns_combine(*args, check_rows=True):
    """
    Combine multiple 1D column vectors or 2D matrices into a single 2D array (column-wise).

    Parameters:
        *args: Each argument can be:
            - A 1D NumPy array or list (treated as a column)
            - A 2D NumPy array or list of lists (multiple columns)
            - None or empty arrays/lists are skipped
        check_rows (bool): If True, all inputs must have the same number of rows (vertical elements)

    Returns:
        np.ndarray: Combined 2D array of shape (n_rows, total_columns)

    Raises:
        ValueError: If an input is a row vector or if row counts mismatch (when check_rows=True)
    """
    cols = []
    row_counts = []

    for i, item in enumerate(args):
        if item is None:
            continue

        try:
            arr = np.asarray(item)
        except Exception as e:
            raise ValueError(f"Input {i} could not be converted to an array — possibly a malformed or ragged list: {item}") from e


        if arr.size == 0:
            continue

        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)

        elif arr.ndim == 2:
            rows, cols_ = arr.shape
            # Reject row vector
            if rows == 1 and cols_ > 1:
                raise ValueError(f"Input {i} looks like a row vector with shape {arr.shape}. "
                                 f"Did you mean to transpose it?")
        else:
            raise ValueError(f"Input {i} has too many dimensions: {arr.shape}")

        cols.append(arr)
        row_counts.append(arr.shape[0])

    if not cols:
        return np.empty((0, 0))

    if check_rows and len(set(row_counts)) != 1:
        raise ValueError(f"Inconsistent number of rows across inputs: {row_counts}")

    try:
        return np.hstack(cols)
    except ValueError as e:
        raise ValueError(f"Column stacking failed — inputs may have inconsistent row counts. "
                        f"Set check_rows=True to catch this early.\nOriginal error: {e}")

def data_bin(data, mode='range', *, dt=None, bin_column=None, returnmode='indices'):
    """
    Bin rows of data based on continuous ranges or discrete values.

    Parameters:
        data (np.ndarray): 2D array of shape (n_rows, n_cols).
        mode (str): 'range' for numeric range binning, 'value' for discrete value binning.
        dt (float, optional): Bin width for 'range' mode (required if mode='range').
        bin_column (int, optional): Column index for 'value' mode (required if mode='value').
        returnmode (str): 'indices' to return bin indices array, 'binned' to return list of arrays per bin.

    Returns:
        If returnmode='indices':
            bin_indices (np.ndarray): Array of shape (n_rows,) assigning each row to a bin index.
                                      Rows outside bins get -1.
            bin_labels (np.ndarray): 
                - For 'range': 1D array of bin edges, length = number_of_bins + 1
                - For 'value': 1D array of unique discrete values used as bins

        If returnmode='binned':
            binned_data (list of np.ndarray): List with one array per bin containing rows in that bin.
            bin_labels (np.ndarray): same as above
    """
    data = np.asarray(data)
    n_rows, n_cols = data.shape

    if mode == 'range':
        if dt is None:
            raise ValueError("Parameter 'dt' must be provided for 'range' mode.")
        
        values = data[:, 0]  # or extend to specify which col later
        vmin = np.floor(np.nanmin(values))
        vmax = np.ceil(np.nanmax(values))
        bin_edges = np.arange(vmin, vmax + dt, dt)

        inds = np.digitize(values, bin_edges, right=False) - 1
        inds[(values < bin_edges[0]) | (values >= bin_edges[-1])] = -1

    elif mode == 'value':
        if bin_column is None:
            raise ValueError("Parameter 'bin_column' must be provided for 'value' mode.")

        values = data[:, bin_column]
        unique_vals = np.unique(values)
        val_to_bin = {val: i for i, val in enumerate(unique_vals)}
        inds = np.array([val_to_bin.get(v, -1) for v in values])

    else:
        raise ValueError(f"Unsupported mode '{mode}'. Use 'range' or 'value'.")

    if returnmode == 'indices':
        return inds, bin_edges if mode == 'range' else unique_vals

    elif returnmode == 'binned':
        # group rows per bin index (skip -1)
        bins = []
        nbins = (len(bin_edges) - 1) if mode == 'range' else len(unique_vals)
        for b in range(nbins):
            bins.append(data[inds == b])
        bin_labels = bin_edges if mode == 'range' else unique_vals
        return bins, bin_labels

    else:
        raise ValueError("returnmode must be either 'indices' or 'binned'")

def dataset_combine(*datasets, avgMode='trapezoidal', dt):
    """
    Merge multiple datasets by time binning and trapezoidal averaging.

    Parameters:
        *datasets: Each dataset is a 2D array-like of shape (n_rows, n_columns),
                   where column 0 is time (in seconds).
        dt (float): Width of time bins.
        avgMode (str): Averaging mode ('arithmetic' or 'trapezoidal').

    Returns:
        tuple: (header: list[str], data: np.ndarray, full_data: list[list])
    """
    import numpy as np

    headers = []
    arrays = []

    for d in datasets:
        # Handle case where header is included (e.g. from CSV)
        if isinstance(d, list) and isinstance(d[0], list) and isinstance(d[0][0], str):
            header_row, d = d[0], d[1:]
            headers.extend(header_row[1:])  # Skip time column
            d = np.array(d, dtype=float)
        else:
            d = np.array(d, dtype=float)
            headers.extend([f"Var{i}" for i in range(1, d.shape[1])])  # fallback names

        arrays.append(d)

    if not arrays:
        return [], np.empty((0, 0)), []

    # Determine bin edges
    t_min = min(np.nanmin(d[:, 0]) for d in arrays)
    t_max = max(np.nanmax(d[:, 0]) for d in arrays)
    bin_edges = np.arange(np.floor(t_min), np.ceil(t_max) + dt, dt)
    n_bins = len(bin_edges) - 1
    t_out = bin_edges[:-1].reshape(-1, 1)  # (n_bins, 1)

    merged_columns = [t_out]

    for data in arrays:
        t = data[:, 0]
        features = data[:, 1:]

        inds = np.digitize(t, bin_edges) - 1
        inds[(t < bin_edges[0]) | (t >= bin_edges[-1])] = -1

        binned_means = np.full((n_bins, features.shape[1]), np.nan)

        for b in range(n_bins):
            mask = inds == b
            if np.any(mask):
                binned_means[b] = average(
                    features[mask],
                    mode=avgMode,
                    time=t[mask]
                )

        merged_columns.append(binned_means)

    data = np.hstack(merged_columns)
    header = ["Time [s]"] + headers

    # Combine header + data for full_data as list-of-lists
    full_data = [header] + data.tolist()

    return header, data, full_data

def dataset_SplitHeaderFromData(dataset):
    """
    Splits the header row from a dataset if present.

    Parameters:
        dataset (list of list): Raw dataset where the first row may be a header.

    Returns:
        tuple: (header, data)
            - header (list or None): The header row if detected, else None.
            - data (list of list): The remaining dataset with only numeric rows.
    """
    if not dataset:
        return None, []

    first_row = dataset[0]

    def is_row_numeric(row):
        try:
            [float(cell) for cell in row]
            return True
        except ValueError:
            return False

    if is_row_numeric(first_row):
        return None, dataset  # No header, all data is numeric
    else:
        return first_row, dataset[1:]  # Header exists

if __name__ == "__main__":
    data = [
        ['ID', 'Value', 'Score'],
        ['1', '1000', '50'],
        ['2', '1500', '60'],
        ['3', '1700', '70'],
        ['4', '1800', '80'],
        ['5', '1900', '90'],
        ['6', '2100', '100'],
    ]

    print("Original data:")
    for row in data:
        print(row)
    print()

    # Test indices mode - remove
    removed_indices = data_remove_rows(data, selector=[1, 3, 4], mode="remove", selection_type="indices")
    print("After removing rows at indices 1, 3, 4:")
    for row in removed_indices:
        print(row)
    print()

    # Test indices mode - keep
    kept_indices = data_remove_rows(data, selector=[2, 4], mode="keep", selection_type="indices")
    print("After keeping only rows at indices 2, 4:")
    for row in kept_indices:
        print(row)
    print()

    # Test range mode - remove with (min, max)
    removed_range = data_remove_rows(data, selector=(1700, 2000), mode="remove", selection_type="range", column=1)
    print("After removing rows where column 1 is in range 1700 to 2000:")
    for row in removed_range:
        print(row)
    print()

    # Test range mode - keep with (min, max)
    kept_range = data_remove_rows(data, selector=(1700, 2000), mode="keep", selection_type="range", column=1)
    print("After keeping rows where column 1 is in range 1700 to 2000:")
    for row in kept_range:
        print(row)
    print()

    # Test range mode - keep with open-ended range (min,)
    kept_open_ended = data_remove_rows(data, selector=(3,), mode="keep", selection_type="range", column=0)
    print("After keeping rows where column 0 >= 3:")
    for row in kept_open_ended:
        print(row)
    print()

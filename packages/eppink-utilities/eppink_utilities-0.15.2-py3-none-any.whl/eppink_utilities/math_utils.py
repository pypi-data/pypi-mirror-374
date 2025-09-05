import numpy as np
import math
from scipy import stats
from scipy.integrate import trapezoid
from .general_utils import validate_inputs

def average(data, mode='arithmetic', weights=None, window=2, time=None):
    """
    Compute column-wise averages over a 2D data array with multiple modes.
    
    Parameters:
        data (array-like): 2D iterable of shape (n_samples, n_features). May contain np.nan, None, or ''.
        mode (str): Averaging mode. Options:
            - 'arithmetic': Simple mean (default)
            - 'weighted': Weighted average (requires `weights`)
            - 'geometric': Geometric mean
            - 'harmonic': Harmonic mean
            - 'median': Median
            - 'mode': Most frequent value
            - 'moving': Moving average (requires `window`)
            - 'trapezoidal': Integral-based average (requires `time`)
        weights (array-like): Optional. Weights for 'weighted' mode.
        window (int): Window size for 'moving' average.
        time (array-like): Time values for 'trapezoidal' mode.

    Returns:
        numpy.ndarray: 1D or 2D array of averages per column. Missing columns → None; partial NaN → skip; all-NaN → np.nan.
    """
    data = np.asarray(data, dtype=object)

    if data.size == 0:
        return np.array([], dtype=object)

    n_rows, n_cols = data.shape if data.ndim == 2 else (len(data), 1)
    results = []

    if mode == 'moving':
        # Moving average returns 2D output
        moving_results = []
        for col in range(n_cols):
            col_data = np.array([x[col] if isinstance(x, (list, tuple, np.ndarray)) else x for x in data], dtype=object)
            valid = np.array([(x if isinstance(x, (int, float, np.number)) and not np.isnan(x) else np.nan) for x in col_data])
            col_result = []
            for i in range(n_rows - window + 1):
                window_vals = valid[i:i + window]
                if np.all(np.isnan(window_vals)):
                    col_result.append(None)
                else:
                    col_result.append(np.nanmean(window_vals))
            moving_results.append(col_result)
        return np.array(moving_results, dtype=object).T

    for col in range(n_cols):
        column = np.array([row[col] if isinstance(row, (list, tuple, np.ndarray)) else row for row in data], dtype=object)
        valid = np.array([
            x if isinstance(x, (int, float, np.number)) and not isinstance(x, bool) and not (isinstance(x, float) and np.isnan(x)) else np.nan
            for x in column
        ], dtype=float)
        valid_mask = ~np.isnan(valid)
        valid_vals = valid[valid_mask]

        if len(valid_vals) == 0:
            if np.all(np.equal(column, None)) or np.all(column == ''):
                results.append(None)
            else:
                results.append(np.nan)
            continue

        if mode == 'arithmetic':
            results.append(np.nanmean(valid_vals))

        elif mode == 'weighted':
            if weights is None:
                raise ValueError("Weights are required for weighted average.")
            w = np.asarray(weights, dtype=float)
            w = w[valid_mask]
            results.append(np.average(valid_vals, weights=w))

        elif mode == 'geometric':
            results.append(stats.gmean(valid_vals))

        elif mode == 'harmonic':
            results.append(stats.hmean(valid_vals))

        elif mode == 'median':
            results.append(np.nanmedian(valid_vals))

        elif mode == 'mode':
            m = stats.mode(valid_vals, nan_policy='omit')
            results.append(m.mode[0] if len(m.mode) else np.nan)

        elif mode == 'trapezoidal':
            if time is None:
                raise ValueError("Time values are required for trapezoidal average.")
            t = np.asarray(time, dtype=float)
            valid_t = t[valid_mask]
            values = valid_vals
            if len(values) < 2:
                results.append(np.nan)
            else:
                integral = trapezoid(values, x=valid_t)
                duration = valid_t[-1] - valid_t[0]
                results.append(integral / duration if duration != 0 else np.nan)

        else:
            raise ValueError(f"Unsupported averaging mode: {mode}")

    return np.array(results, dtype=object)

def safe_divide(numerator, denominator, warnings=False):
    """
    Safely divide two numbers (scalars, arrays, or combinations thereof),
    avoiding division by zero or invalid operations and propagating NaNs
    from numerator or denominator.

    Parameters:
    ----------
    numerator : float, int, array-like
        The numerator(s) in the division.
    denominator : float, int, array-like
        The denominator(s) in the division.
    warnings: bool
        When True, prints warnings to the terminal

    Returns:
    -------
    result : float or np.ndarray
        The result of the division. Any division by zero or invalid result
        (e.g., inf, -inf, nan) is replaced with np.nan.
        Also, if numerator or denominator is NaN at any position, result is NaN there.

    """
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)

    # Detect division by zero positions before division
    zero_div_mask = (denominator == 0)

    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.true_divide(numerator, denominator)

    # Create a mask where numerator or denominator is nan
    nan_mask = np.isnan(numerator) | np.isnan(denominator)

    # Also replace inf, -inf, and nan in result with nan
    invalid_mask = ~np.isfinite(result)

    # Combine masks so that all invalid places are nan
    combined_mask = nan_mask | invalid_mask

    if np.any(zero_div_mask):
        if warnings == True:
            print("Error: Division by zero encountered.")

    if np.isscalar(result):
        if combined_mask:
            return np.nan
        return result

    result[combined_mask] = np.nan

    return result

def derivative_FDM(y, x, derivative, accuracy):
    """
    Compute the finite difference derivative of a function with uniform spacing.
    
    Parameters:
        y : np.ndarray
            Vector of function values.
        x : np.ndarray
            Vector of grid points (must be uniformly spaced).
        derivative : int
            Order of the derivative to compute (e.g., 1 for first derivative).
        accuracy : int
            Desired order of accuracy (e.g., 2 for O(h^2)).
    
    Returns:
        dy_dx : np.ndarray
            Vector of the derivative values at each point.
        x_used : np.ndarray
            Possibly trimmed x corresponding to dy_dx.
        error_term : str
            The truncation error term in big-O notation, e.g., "O(h^2)".
        error_estimation : n
            
    """

    CD_COEFFS = {
    (1, 2):  [ -0.5, 0, 0.5 ],
    (1, 4):  [ 1/12, -2/3, 0, 2/3, -1/12 ],
    (1, 6):  [ -1/60, 3/20, -3/4, 0, 3/4, -3/20, 1/60 ],
    (1, 8):  [ 1/280, -4/105, 1/5, -4/5, 0, 4/5, -1/5, 4/105, -1/280 ],
    (2, 2):  [ 1, -2, 1 ],
    (2, 4):  [ -1/12, 4/3, -5/2, 4/3, -1/12 ],
    (2, 6):  [ 1/90, -3/20, 3/2, -49/18, 3/2, -3/20, 1/90 ],
    (2, 8):  [ -1/560, 8/315, -1/5, 8/5, -205/72, 8/5, -1/5, 8/315, -1/560 ],
    (3, 2):  [ -0.5, 1, 0, -1, 0.5 ],
    (3, 4):  [ 1/8, -1, 13/8, 0, -13/8, 1, -1/8 ],
    (3, 6):  [ -7/240, 3/10, -169/120, 61/30, 0, -61/30, 169/120, -3/10, 7/240 ],
    (4, 2):  [ 1, -4, 6, -4, 1 ],
    (4, 4):  [ -1/6, 2, -13/2, 28/3, -13/2, 2, -1/6 ],
    (4, 6):  [ 7/240, -2/5, 169/60, -122/15, 91/8, -122/15, 169/60, -2/5, 7/240 ]
}
    
    FD_COEFFS = {
    (1, 1): [-1, 1],
    (1, 2): [-3/2, 2, -1/2],
    (1, 3): [-11/6, 3, -3/2, 1/3],
    (1, 4): [-25/12, 4, -3, 4/3, -1/4],
    (1, 5): [-137/60, 5, -5, 10/3, -5/4, 1/5],
    (1, 6): [-49/20, 6, -15/2, 20/3, -15/4, 6/5, -1/6],
    (2, 1): [1, -2, 1],
    (2, 2): [2, -5, 4, -1],
    (2, 3): [35/12, -26/3, 19/2, -14/3, 11/12],
    (2, 4): [15/4, -77/6, 107/6, -13, 61/12, -5/6],
    (2, 5): [203/45, -87/5, 117/4, -254/9, 33/2, -27/5, 137/180],
    (2, 6): [469/90, -223/10, 879/20, -949/18, 41, -201/10, 1019/180, -7/10],
    (3, 1): [-1, 3, -3, 1],
    (3, 2): [-5/2, 9, -12, 7, -3/2],
    (3, 3): [-17/4, 71/4, -59/2, 49/2, -41/4, 7/4],
    (3, 4): [-49/8, 29, -461/8, 62, -307/8, 13, -15/8],
    (4, 1): [1, -4, 6, -4, 1],
    (4, 2): [3, -14, 26, -24, 11, -2],
    (4, 3): [35/6, -31, 137/2, -242/3, 107/2, -19, 17/6],
    (4, 4): [28/3, -111/2, 142, -1219/6, 176, -185/2, 82/3, -7/2],
}
    
    def CD(y, x, derivative=1, accuracy=4):
        """
        Central finite difference derivative calculation.
        
        Parameters:
            y : array_like
                Function values at discrete points.
            x : array_like
                Grid points (must be uniform).
            derivative : int
                Derivative order (1, 2, 3, 4).
            accuracy : int
                Order of accuracy (2, 4, 6, 8).
        
        Returns:
            dydx : ndarray
                Derivative array, only for valid central points.
        """
        y = np.asarray(y)
        x = np.asarray(x)
        h = x[1] - x[0]
        

        key = (derivative, accuracy)
        if key not in CD_COEFFS:
            raise ValueError(f"Unsupported derivative={derivative}, accuracy={accuracy}")

        coeffs = np.array(CD_COEFFS[key])
        stencil_size = len(coeffs)
        offset = stencil_size // 2

        dydx = np.full_like(y, np.nan, dtype=float)

        # Apply stencil at interior points
        for i in range(offset, len(y) - offset):
            window = y[i - offset:i + offset + 1]
            dydx[i] = np.dot(coeffs, window) / (h ** derivative)

        return dydx

    def FD(y, x, derivative=1, accuracy=4):
        """
        Forward finite difference derivative calculation (for uniform grids).
        
        Parameters:
            y : array_like
                Function values at discrete points.
            x : array_like
                Grid points (must be uniform).
            derivative : int
                Derivative order (1, 2, 3, 4).
            accuracy : int
                Order of accuracy (1, 2, ..., 6).
        
        Returns:
            dydx : ndarray
                Derivative array, only at valid forward points (rest are NaN).
        """
        y = np.asarray(y)
        x = np.asarray(x)
        h = x[1] - x[0]
        


        key = (derivative, accuracy)
        if key not in FD_COEFFS:
            raise ValueError(f"Unsupported derivative={derivative}, accuracy={accuracy}")

        coeffs = np.array(FD_COEFFS[key])
        stencil_size = len(coeffs)

        dydx = np.full_like(y, np.nan, dtype=float)

        for i in range(len(y) - stencil_size + 1):
            window = y[i:i + stencil_size]
            dydx[i] = np.dot(coeffs, window) / (h ** derivative)

        return dydx

    def BD(y, x, derivative=1, accuracy=4):
        """
        Backward finite difference derivative calculation (for uniform grids).
        
        Parameters:
            y : array_like
                Function values at discrete points.
            x : array_like
                Grid points (must be uniform).
            derivative : int
                Derivative order (1, 2, 3, 4).
            accuracy : int
                Order of accuracy (1, 2, ...).
        
        Returns:
            dydx : ndarray
                Derivative array, only at valid backward points (rest are NaN).
        """
        y = np.asarray(y)
        x = np.asarray(x)
        h = x[1] - x[0]


        key = (derivative, accuracy)
        if key not in FD_COEFFS:
            raise ValueError(f"Unsupported derivative={derivative}, accuracy={accuracy}")

        coeffs = -np.array(FD_COEFFS[key])[::-1]  # Reverse to align with y[i - n: i + 1]
        stencil_size = len(coeffs)

        dydx = np.full_like(y, np.nan, dtype=float)

        for i in range(stencil_size - 1, len(y)):
            window = y[i - stencil_size + 1:i + 1]
            dydx[i] = np.dot(coeffs, window) / (h ** derivative)

        return dydx

    # === 1. Uniform spacing check ===
    h_arr = np.diff(x)
    if not np.allclose(h_arr, h_arr[0]):
        raise ValueError("Non-uniform spacing detected. This method only supports uniform grids.")
    h = h_arr[0]

    # === 2. Check accuracy support ===
    available_keys = set(FD_COEFFS.keys())
    if (derivative, accuracy) not in available_keys:
        raise ValueError(f"Accuracy {accuracy} not available for derivative order {derivative}.")

    # === 3. Compute derivatives using each method vectorized ===
    dydx_fd = FD(y, x, derivative, accuracy)
    dydx_bd = BD(y, x, derivative, accuracy)
    dydx_cd = CD(y, x, derivative, accuracy)

    # === 4. Combine results to final output ===
    coeffs_cd = np.array(CD_COEFFS[(derivative, accuracy)])
    half_width = len(coeffs_cd) // 2
    n = len(y)

    dy_dx = np.full_like(y, np.nan, dtype=float)

    # Forward difference at start
    dy_dx[:half_width] = dydx_fd[:half_width]

    # Backward difference at end
    dy_dx[-half_width:] = dydx_bd[-half_width:]

    # Central difference in the middle
    dy_dx[half_width:n - half_width] = dydx_cd[half_width:n - half_width]

    error_est = safe_divide((x[1] - x[0]) ** accuracy, math.factorial(accuracy)) * y ** (derivative + accuracy) 

    # === 5. Return values ===
    error_term = f"O(h^{accuracy})"
    return dy_dx, x, error_term, error_est

def error_catastrophic_cancellation(x, y, deltax, deltay):
    """
    Estimate the relative error in a subtraction due to catastrophic cancellation.
    
    Parameters:
        x : float or np.ndarray
            First approximate value(s).
        y : float or np.ndarray
            Second approximate value(s).
        deltax : float or np.ndarray
            Relative error(s) in x (i.e., delta_x / x).
        deltay : float or np.ndarray
            Relative error(s) in y (i.e., delta_y / y).
    
    Returns:
        rel_error : float or np.ndarray
            Estimated relative error in the computed difference (x - y) due to cancellation,
            given by |x * deltax - y * deltay| / |x - y|.
    """

    x, y, deltax, deltay = validate_inputs(x, y, deltax, deltay, check_broadcast=True, scalars_to_arrays=True)
    rel_error = safe_divide(np.abs(x * deltax - y * deltay), np.abs(x - y))
    return rel_error



if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    # Define test function and its true derivative
    def f(x):
        return np.sin(x)

    def df_exact(x):
        return np.cos(x)

    # Grid settings
    x = np.linspace(0, 2 * np.pi, 100)
    y = f(x)

    # Choose derivative and accuracy
    derivative = 1
    accuracy = 4

    # Compute finite difference derivative
    dy_dx, x_used, error_term, error_estimation = derivative_FDM(y, x, derivative, accuracy)

    # Exact derivative
    dy_dx_exact = df_exact(x)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(x, dy_dx_exact, label="Exact derivative", linewidth=2)
    plt.plot(x_used, dy_dx, label=f"FD derivative ({error_term})", linestyle="--")
    plt.title("Comparison of Exact and Finite Difference Derivative")
    plt.xlabel("x")
    plt.ylabel("dy/dx")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Plot error
    plt.figure(figsize=(10, 4))
    plt.plot(x, dy_dx - dy_dx_exact, label="Error", color="red")
    plt.title("Derivative Error (FD - Exact)")
    plt.xlabel("x")
    plt.ylabel("Error")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Print numerical error at boundaries
    print("Boundary errors:")
    print("Start (first 5):", dy_dx[:5] - dy_dx_exact[:5])
    print("End (last 5):", dy_dx[-5:] - dy_dx_exact[-5:])

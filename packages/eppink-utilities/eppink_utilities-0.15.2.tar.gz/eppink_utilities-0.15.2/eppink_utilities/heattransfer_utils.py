import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
import warnings
from .math_utils import derivative_FDM
from .math_utils import safe_divide
from .general_utils import validate_inputs
from .dimless_utils import grashof, prandtl, rayleigh

def conduction_radial_steady_numerical(r, L, bc, k, gridpoints, solver="RK45", tol=1e-3):
    """
    Solve steady-state radial heat conduction in a cylinder numerically with possible temperature-dependent thermal conductivity.

    Parameters
    ----------
    r : tuple of floats
        Radial domain as (r0, R), inner and outer radii.
    L : float
        Axial length of the cylinder (used to calculate cylindrical surface area).
    bc : tuple
        Boundary conditions at r0 as (T0, T1_input, Q):
        - T0: Temperature at inner radius r0.
        - T1_input: Temperature gradient dT/dr at r0 (can be None if unknown).
        - Q: Heat flux at r0 (can be None if unknown).
        Exactly one of T1_input or Q must be provided, or both must be consistent.
    k : float or array-like
        Thermal conductivity. Can be:
        - A constant float or int.
        - An array-like [[T0, k0], [T1, k1], ...] specifying temperature-dependent conductivity,
          which is interpolated internally.
    gridpoints : int
        Number of points in radial mesh for numerical solution.
    solver : str, optional
        ODE solver method for scipy.integrate.solve_ivp (default "RK45").
    tol : float, optional
        Relative tolerance for heat flux conservation check (default 1e-3).

    Returns
    -------
    array like
        r_vals, T_vals, dTdr_vals, Q_error

    Description
    -----------
    Solves the nonlinear ODE system describing steady radial heat conduction in a cylinder:

        d/dr [k(T) * A(r) * dT/dr] = 0,

    where A(r) = 2 * pi * r * L is the cylindrical surface area.

    The equation expands to:

        d²T/dr² + (1/k) * (dk/dT) * (dT/dr)² + (1/r) * dT/dr = 0,

    with boundary conditions at the inner radius r0:

        T(r0) = T0,
        and either specified temperature gradient dT/dr(r0) = T1_input
        or specified heat flux Q = -k * A(r0) * dT/dr(r0).

    The function supports temperature-dependent thermal conductivity via interpolation,
    and integrates the ODE system numerically using solve_ivp.

    It verifies heat flux conservation between inner and outer boundaries and warns
    if the flux discrepancy exceeds the specified tolerance.

    Symmetry condition at r=0 is handled by setting the second derivative of temperature to zero.

    Warnings are issued if the ODE solver fails or if boundary fluxes are inconsistent.

    This method is suitable for modeling steady heat conduction in cylindrical coordinates
    with radial dependence and non-constant thermal conductivity.
    """

    r0, R = r
    T0, T1_input, Q = bc

    # Detect constant or interpolated k(T)
    if isinstance(k, (float, int)):
        k_const = float(k)
        def k_interp(T): return k_const
        def dk_interp(T): return 0.0
    else:
        k = np.asarray(k)
        k_interp = interp1d(k[:, 0], k[:, 1], kind='cubic', fill_value="extrapolate")
        T_fine = np.linspace(k[:, 0].min(), k[:, 0].max(), 1000)
        dk_dT_fine = np.gradient(k_interp(T_fine), T_fine)
        dk_interp = interp1d(T_fine, dk_dT_fine, kind='linear', fill_value="extrapolate")

    def area(r): return 2 * np.pi * r * L

    # Compute initial dT/dr with corrected minus sign
    if T1_input is None and Q is not None:
        A0 = area(r0)
        k0 = k_interp(T0)
        T1 = - Q / (k0 * A0)  # <- corrected minus sign
    elif Q is None and T1_input is not None:
        T1 = T1_input
    elif Q is not None and T1_input is not None:
        A0 = area(r0)
        k0 = k_interp(T0)
        expected_T1 = - Q / (k0 * A0)  # corrected minus sign
        if not np.isclose(T1_input, expected_T1, rtol=1e-4):
            raise ValueError("Inconsistent values: T'0 and Q do not satisfy dT/dr = -Q / (k(T) * A(r))")
        T1 = T1_input
    else:
        raise ValueError("Must provide either dT/dr or Q in bc")

    def system(r, y):
        T, dTdr = y
        k_val = k_interp(T)
        dk_dT_val = dk_interp(T)
        if r == 0:
            d2Tdr2 = 0  # symmetry condition
        else:
            d2Tdr2 = - (1 / k_val) * dk_dT_val * dTdr**2 - (1 / r) * dTdr
        return [dTdr, d2Tdr2]

    r_span = (r0, R)
    r_eval = np.linspace(r0, R, gridpoints)
    y0 = [T0, T1]

    sol = solve_ivp(system, r_span, y0, method=solver, t_eval=r_eval)

    if not sol.success:
        warnings.warn("ODE solver failed: " + sol.message)

    T_vals = sol.y[0]
    dTdr_vals = sol.y[1]
    r_vals = sol.t

    # Compute Q at r0 and r=R from numerical solution
    A_r0 = area(r0)
    k_r0 = k_interp(T_vals[0])
    Q_r0_calc = - k_r0 * A_r0 * dTdr_vals[0]

    A_R = area(R)
    k_R = k_interp(T_vals[-1])
    Q_R_calc = - k_R * A_R * dTdr_vals[-1]
    Q_error = Q_r0_calc - Q_R_calc

    # Check flux consistency
    if np.abs(Q_error) > tol * np.abs(Q_r0_calc):
        warnings.warn(f"Flux inconsistency: Q(r0)={Q_r0_calc:.4f}, Q(R)={Q_R_calc:.4f}")


    return r_vals, T_vals, dTdr_vals, Q_error

def conduction_cartesian_steady_numerical(x, A, bc, k, gridpoints, solver="RK45", tol=1e-3):
    """
    Solve steady-state 1D Cartesian heat conduction with temperature-dependent thermal conductivity.

    Parameters
    ----------
    x : tuple of floats
        Domain in x-direction as (x0, x1).
    A : float
        Cross-sectional area (constant in Cartesian geometry).
    bc : tuple
        Boundary conditions at x0 as (T0, T1_input, Q):
        - T0: Temperature at x0.
        - dTdx: Temperature gradient dT/dx at x0 (can be None if unknown).
        - Q: Heat flux at x0 (can be None if unknown).
        Exactly one of dTdx or Q must be provided, or both must be consistent.
    k : float or array-like
        Thermal conductivity. Can be:
        - A constant float or int.
        - An array-like [[T0, k0], [T1, k1], ...] for T-dependent k, interpolated internally.
    gridpoints : int
        Number of points in x-direction for solution.
    solver : str, optional
        ODE solver method for scipy.integrate.solve_ivp.
    tol : float, optional
        Tolerance for flux mismatch warning.

    Returns
    -------
    array-like
        x_vals, T_vals, dTdx_vals, Q_error
    """

    x0, x1 = x
    T0, dTdx, Q = bc

    if isinstance(k, (float, int)):
        k_const = float(k)
        def k_interp(T): return k_const
        def dk_interp(T): return 0.0
    else:
        k = np.asarray(k)
        k_interp = interp1d(k[:, 0], k[:, 1], kind='cubic', fill_value="extrapolate")
        T_fine = np.linspace(k[:, 0].min(), k[:, 0].max(), 1000)
        dk_dT_fine = np.gradient(k_interp(T_fine), T_fine)
        dk_interp = interp1d(T_fine, dk_dT_fine, kind='linear', fill_value="extrapolate")

    if dTdx is None and Q is not None:
        k0 = k_interp(T0)
        T1 = - Q / (k0 * A)
    elif Q is None and dTdx is not None:
        T1 = dTdx
    elif Q is not None and dTdx is not None:
        k0 = k_interp(T0)
        expected_T1 = - Q / (k0 * A)
        if not np.isclose(dTdx, expected_T1, rtol=1e-4):
            raise ValueError("Inconsistent values: T'0 and Q do not satisfy dT/dx = -Q / (k(T) * A)")
        T1 = dTdx
    else:
        raise ValueError("Must provide either dT/dx or Q in bc")

    def system(x, y):
        T, dTdx = y
        k_val = k_interp(T)
        dk_dT_val = dk_interp(T)
        d2Tdx2 = - (dk_dT_val / k_val) * dTdx**2
        return [dTdx, d2Tdx2]

    x_span = (x0, x1)
    x_eval = np.linspace(x0, x1, gridpoints)
    y0 = [T0, T1]

    sol = solve_ivp(system, x_span, y0, method=solver, t_eval=x_eval)

    if not sol.success:
        warnings.warn("ODE solver failed: " + sol.message)

    T_vals = sol.y[0]
    dTdx_vals = sol.y[1]
    x_vals = sol.t

    # Compute heat flux at both ends
    k_x0 = k_interp(T_vals[0])
    Q_x0_calc = - k_x0 * A * dTdx_vals[0]

    k_x1 = k_interp(T_vals[-1])
    Q_x1_calc = - k_x1 * A * dTdx_vals[-1]

    Q_error = Q_x0_calc - Q_x1_calc

    if np.abs(Q_error) > tol * np.abs(Q_x0_calc):
        warnings.warn(f"Flux inconsistency: Q(x0)={Q_x0_calc:.4f}, Q(x1)={Q_x1_calc:.4f}")

    return x_vals, T_vals, dTdx_vals, Q_error


def conduction_radial_analytical(
    radii,
    T_bounds,
    k_data_list,
    N_points_per_layer,
    L=1.0
):
    """
    Analytical solution for radial conduction in a multi-layered cylinder.

    Returns
    -------
    sol_guess : array like
        r_all, T_all, Q_dot, q_dot, dT_dr
    """
    n = len(k_data_list)
    T1, Tn1 = T_bounds

    # Compute average temperature per layer (linear interpolation in log space)
    ln_r = np.log(radii)
    T_interface = np.interp(ln_r, [ln_r[0], ln_r[-1]], [T1, Tn1])

    k_avgs = []
    for i in range(n):
        T_avg = 0.5 * (T_interface[i] + T_interface[i + 1])
        k_data = k_data_list[i]

        if np.isscalar(k_data):
            k_avg = float(k_data)
        else:
            T_vals, k_vals = k_data[:, 0], k_data[:, 1]
            k_interp = interp1d(T_vals, k_vals, kind='linear', fill_value='extrapolate')
            k_avg = float(k_interp(T_avg))

        k_avgs.append(k_avg)

    # Compute total thermal resistance and heat flow Q_dot
    resistances = [np.log(radii[i + 1] / radii[i]) / (2 * np.pi * L * k_avgs[i]) for i in range(n)]
    R_tot = sum(resistances)
    Q_dot = (T1 - Tn1) / R_tot

    # Build temperature profile T(r)
    r_all = []
    T_all = []
    k_all = []

    T_start = T1
    for i in range(n):
        r0, r1 = radii[i], radii[i + 1]
        k = k_avgs[i]
        N = N_points_per_layer[i]

        r_layer = np.linspace(r0, r1, N) if i == 0 else np.linspace(r0, r1, N)[1:]
        T_layer = T_start - (Q_dot / (2 * np.pi * L * k)) * np.log(r_layer / r0)
        T_start = T_layer[-1]

        r_all.append(r_layer)
        T_all.append(T_layer)
        k_all.append(np.full_like(r_layer, k))

    r_all = np.concatenate(r_all)
    T_all = np.concatenate(T_all)
    k_all = np.concatenate(k_all)

    def compute_gradients_per_layer_forward_diff(r_all, T_all, k_all, radii, N_points_per_layer):
        dT_dr = np.empty_like(T_all)
        q_dot = np.empty_like(T_all)
        
        start_idx = 0
        n_layers = len(N_points_per_layer)
        
        for i in range(n_layers):
            if i == 0:
                N = N_points_per_layer[i]
            else:
                N = N_points_per_layer[i] - 1  # skip overlapping first point
            
            end_idx = start_idx + N
            
            r_layer = r_all[start_idx:end_idx]
            T_layer = T_all[start_idx:end_idx]
            k_layer = k_all[start_idx:end_idx]
            
            # Forward difference for gradient
            dT_dr_layer = (T_layer[1:] - T_layer[:-1]) / (r_layer[1:] - r_layer[:-1])
            
            dT_dr_layer_full = np.empty(N)
            dT_dr_layer_full[:-1] = dT_dr_layer
            dT_dr_layer_full[-1] = dT_dr_layer[-1]
            
            dT_dr[start_idx:end_idx] = dT_dr_layer_full
            q_dot[start_idx:end_idx] = -k_layer * dT_dr_layer_full
            
            start_idx = end_idx
        
        return dT_dr, q_dot

    dT_dr, q_dot = compute_gradients_per_layer_forward_diff(r_all, T_all, k_all, radii, N_points_per_layer)


    return r_all, T_all, Q_dot, q_dot, dT_dr

def Nusselt_correlations_free(mode, *, Ra=None, Gr=None, Pr = None, d=None, L=None):
    """
    Computes the Nusselt number (Nu) using empirical correlations for natural convection
    in several geometries, based on the selected mode.

    Parameters:
    ----------
    mode : str
        The correlation mode. Supported options are:
        
        - "Annulus_vertical_1": 
            Empirical correlation for natural convection in vertical annuli.
            Equation:
                Nu = 0.761 * (Ra * d / L)^0.283
            Valid for:
                10 < (Ra * d / L) < 1e3
            Source:
                Kubair & Simha (Exact citation/details TBD).
        
        - "Annulus_vertical_2":
            Alternative empirical correlation for vertical annuli.
            Equation:
                Nu = 0.398 * (Ra * d / L)^0.284
            Valid for:
                10 < (Ra * d / L) < 1e5
            Source:
                Kubair & Simha (Exact citation/details TBD).

    Keyword Arguments:
    ------------------
    Ra : float
        Rayleigh number (dimensionless), representing buoyancy-driven flow.
    d : float
        Gap between the inner and outer cylinders (in meters) d = r_o - r_i.
    L : float
        Characteristic length or height of the annular region (in meters).

    Returns:
    -------
    Nu : float
        Computed Nusselt number based on the selected mode and input parameters.

    Raises:
    ------
    ValueError:
        - If any of Ra, d, or L is not provided.
        - If the provided mode is not supported.
    
    Warnings:
    --------
    Issues a warning if the computed Ra*d/L value is outside the valid range for
    the selected correlation mode.

    Notes:
    -----
    The Nusselt number quantifies convective heat transfer relative to conduction.
    These correlations are based on experimental/numerical results and must be applied
    only within their validity range for physically meaningful results.
    """


    if mode == "Annulus_vertical_1":
        if Ra is None or d is None or L is None:
            raise ValueError("Ra, d, and L must all be provided.")
        Ra, d, L = validate_inputs(Ra, d, L, check_broadcast=True)
        ratio = Ra * safe_divide(d, L)
        if not (10 < ratio < 1e3):
            warnings.warn("Ra*d/L is out of the valid range (10 < Ra*d/L < 1e3) for Annulus_vertical_1.")
        Nu = 0.761 * (ratio) ** 0.283
        return Nu

    elif mode == "Annulus_vertical_2":
        if Ra is None or d is None or L is None:
            raise ValueError("Ra, d, and L must all be provided.")
        Ra, d, L = validate_inputs(Ra, d, L, check_broadcast=True)
        ratio = Ra * safe_divide(d, L)
        if not (10 < ratio < 1e5):
            warnings.warn("Ra*d/L is out of the valid range (10 < Ra*d/L < 1e5) for Annulus_vertical_2.")
        Nu = 0.398 * (ratio) ** 0.284
        return Nu

    else:
        raise ValueError(f"Unknown mode '{mode}'. Please choose a supported mode.")

def convection_analytical(
    T_a,
    A,
    d,
    L,
    T_eval,
    beta,
    mu,
    rho,
    cp,
    k,
    nusselt_func,
    *,
    mode="solve_T",
    Q=None,
    T_b=None,
    g=9.81,
    max_iter=50,
    tol=1e-4,
):
    """
    Solves for T_b or Q in a free convection heat transfer problem.

    Parameters
    ----------
    T_a : float or np.ndarray
        Ambient temperature [K]
    A : float
        Surface area [m^2]
    d : float
        Characteristic length [m]
    L : float
        Vertical length [m]
    T_eval : array-like
        Temperature values corresponding to the property vectors
    beta, mu, rho, cp, k : array-like
        Thermophysical property vectors
    nusselt_func : callable
        Function to compute Nu, must accept Gr, Pr, Ra, d, L
    mode : str
        'solve_T' to compute T_b (requires Q),
        'solve_Q' to compute Q (requires T_b)
    Q : float or np.ndarray, optional
        Heat transfer rate [W] (required for mode='solve_T')
    T_b : float or np.ndarray, optional
        Surface temperature [K] (required for mode='solve_Q')
    g : float, optional
        Gravitational acceleration [m/s^2] (default is 9.81)
    max_iter : int, optional
        Maximum number of iterations (only used in mode='solve_T')
    tol : float, optional
        Convergence tolerance (only used in mode='solve_T')

    Returns
    -------
    results including:
    - Q_solved,  
        T_a,       
        T_b,      
        T_avg,   
        h,        
        Nu,      
        Ra,       
        Gr,      
        Pr        
    """

    def check_positive_properties(beta_i, mu_i, rho_i, cp_i, k_i, nu_i, d):
        if beta_i <= 0:
            raise ValueError(f"Invalid beta (thermal expansion coefficient): {beta_i}. Expected > 0.")
        if mu_i <= 0:
            raise ValueError(f"Invalid dynamic viscosity (mu): {mu_i}. Expected > 0.")
        if rho_i <= 0:
            raise ValueError(f"Invalid density (rho): {rho_i}. Expected > 0.")
        if cp_i <= 0:
            raise ValueError(f"Invalid specific heat capacity (cp): {cp_i}. Expected > 0.")
        if k_i <= 0:
            raise ValueError(f"Invalid thermal conductivity (k): {k_i}. Expected > 0.")
        if nu_i <= 0:
            raise ValueError(f"Invalid kinematic viscosity (nu): {nu_i}. Expected > 0.")
        if d <= 0:
            raise ValueError(f"Invalid characteristic length (d): {d}. Expected > 0.")
        
    # Prepare interpolation functions
    interp = lambda arr: interp1d(T_eval, arr, kind='linear', fill_value='extrapolate')
    interp_beta = interp(beta)
    interp_mu   = interp(mu)
    interp_rho  = interp(rho)
    interp_cp   = interp(cp)
    interp_k    = interp(k)

    if mode == "solve_T":
        if Q is None:
            raise ValueError("Q must be provided for mode='solve_T'")

        # Initial guess
        h = 10
        T_b = T_a - Q / (h * A)
        for _ in range(max_iter):
            T_avg = 0.5 * (T_a + T_b)
            # warning 
            if not (T_eval[0] <= T_avg <= T_eval[-1]):
                warnings.warn(f"T_avg={T_avg:.2f} is outside the interpolation range. Extend T_eval")

            # Interpolate properties
            beta_i = interp_beta(T_avg)
            mu_i   = interp_mu(T_avg)
            rho_i  = interp_rho(T_avg)
            cp_i   = interp_cp(T_avg)
            k_i    = interp_k(T_avg)
            nu_i = mu_i/rho_i
            check_positive_properties(beta_i, mu_i, rho_i, cp_i, k_i, nu_i, d)
            Gr = grashof(g, d, nu=nu_i, beta=beta_i, Ts=T_a, T_inf=T_b, mode="heat")
            Pr = prandtl(cp_i, mu_i, k_i,)
            Ra = rayleigh(Gr=Gr,Pr=Pr,mode="grpr")
            Nu = nusselt_func(Gr=Gr, Pr=Pr, Ra=Ra, d=d, L=L)
            h_new = Nu * k_i / d
            T_b_new = T_a - Q / (h_new * A)

            if np.all(np.abs(T_b_new - T_b) < tol):
                break

            T_b = T_b_new
            h = h_new
        else:
            warnings.warn("convection_analytical: Maximum iterations reached without convergence.")

        T_avg = 0.5 * (T_a + T_b)
        Q_solved = Q  # Preserve original input

    elif mode == "solve_Q":
        if T_b is None:
            raise ValueError("T_b must be provided for mode='solve_Q'")

        T_avg = 0.5 * (T_a + T_b)

        # Interpolate properties
        beta_i = interp_beta(T_avg)
        mu_i   = interp_mu(T_avg)
        rho_i  = interp_rho(T_avg)
        cp_i   = interp_cp(T_avg)
        k_i    = interp_k(T_avg)
        nu_i = mu_i / rho_i
        check_positive_properties(beta_i, mu_i, rho_i, cp_i, k_i, nu_i)


        Gr = grashof(g, d, nu_i, beta=beta_i, Ts=T_a, T_inf=T_b, mode="heat")
        Pr = prandtl(cp_i, mu_i, k_i,)
        Ra = rayleigh(Gr=Gr,Pr=Pr,mode="grpr")

        Nu = nusselt_func(Gr=Gr, Pr=Pr, Ra=Ra, d=d, L=L)
        h = Nu * k_i / d
        Q_solved = h * A * (T_a - T_b)

    else:
        raise ValueError(f"Unknown mode '{mode}'. Use 'solve_T' or 'solve_Q'.")
 
    return (
        Q_solved,  # Q
        T_a,       # T_a
        T_b,       # T_b
        T_avg,     # T_avg
        h,         # h
        Nu,        # Nu
        Ra,        # Ra
        Gr,        # Gr
        Pr         # Pr
    )

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    # Define temperature-dependent thermal conductivity: k(T) = 10 + 0.5 * T
    # As an array for interpolation: [[T0, k0], [T1, k1], ...]
    T_k_array = np.array([
        [0, 60],
        [100, 60],
        [200, 60],
        [300, 60],
        [400, 60]
    ])

    # Domain and area
    x = (0, 0.1)  # meters
    A = 0.01             # m² cross-sectional area
    gridpoints = 200

    # --- Test Case 1: Provide T0 and dT/dx ---
    T0 = 100  # deg C
    T1_input = -500  # dT/dx in deg C/m (cooling direction)
    Q = None  # unknown

    bc1 = (T0, T1_input, Q)

    x_vals1, T_vals1, dTdx_vals1, Q_error1 = conduction_cartesian_steady_numerical(
        x=x,
        A=A,
        bc=bc1,
        k=5,
        gridpoints=gridpoints
    )

    print("\n--- Test Case 1: T0 and dT/dx specified ---")
    print(f"Max Temperature: {np.max(T_vals1):.2f} °C")
    print(f"Min Temperature: {np.min(T_vals1):.2f} °C")
    print(f"Heat flux discrepancy: {Q_error1:.6f} W")

    # --- Test Case 2: Provide T0 and Q ---
    T0 = 100  # deg C
    Q = -T1_input * A * 60  # W (heat added at x=0)
    T1_input = None

    bc2 = (T0, T1_input, Q)

    x_vals2, T_vals2, dTdx_vals2, Q_error2 = conduction_cartesian_steady_numerical(
        x=x,
        A=A,
        bc=bc2,
        k=T_k_array,
        gridpoints=gridpoints
    )

    print("\n--- Test Case 2: T0 and Q specified ---")
    print(f"Max Temperature: {np.max(T_vals2):.2f} °C")
    print(f"Min Temperature: {np.min(T_vals2):.2f} °C")
    print(f"Heat flux discrepancy: {Q_error2:.6f} W")

    # --- Plotting ---
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals1, T_vals1, label="Case 1: T0 & dT/dx")
    plt.plot(x_vals2, T_vals2, label="Case 2: T0 & Q", linestyle='--')
    plt.xlabel("x [m]")
    plt.ylabel("Temperature [°C]")
    plt.title("Steady-State 1D Heat Conduction with k(T)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

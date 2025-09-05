import numpy as np
from .general_utils import validate_inputs
from .math_utils import safe_divide

def archimedes(g, L, rho, rho_l, *, mode="dynamic", nu=None, mu=None):
    """
    Calculates the Archimedes number (Ar), a dimensionless number representing 
    the ratio of gravitational forces to viscous forces.

    Formulas:
        - Kinematic mode:
            Ar = g * L**3 * ((rho - rho_l) / rho_l) / nu**2
        - Dynamic mode:
            Ar = g * L**3 * rho_l * (rho - rho_l) / mu**2

    Parameters:
        g : float or array-like
            Gravitational acceleration (m/s²)
        L : float or array-like
            Characteristic length (m)
        rho : float or array-like
            Density of the body (kg/m³)
        rho_l : float or array-like
            Density of the fluid (kg/m³)
        mode : str, optional (default: 'dynamic')
            Calculation mode: 'kinematic' or 'dynamic'
        nu : float or array-like, required for 'kinematic' mode
            Kinematic viscosity (m²/s)
        mu : float or array-like, required for 'dynamic' mode
            Dynamic viscosity (Pa·s)

    Returns:
        Ar : float or ndarray
            Archimedes number. Propagates np.nan if any input is np.nan.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    g, L, rho, rho_l = validate_inputs(g, L, rho, rho_l)

    if mode == "kinematic":
        if nu is None:
            raise ValueError("Kinematic viscosity 'nu' must be provided for mode='kinematic'")
        nu, = validate_inputs(nu)
        numerator = g * L**3 * safe_divide((rho - rho_l), rho_l)
        return safe_divide(numerator, nu**2)

    elif mode == "dynamic":
        if mu is None:
            raise ValueError("Dynamic viscosity 'mu' must be provided for mode='dynamic'")
        mu, = validate_inputs(mu)
        numerator = g * L**3 * rho_l * (rho - rho_l)
        return safe_divide(numerator, mu**2)

    else:
        raise ValueError("Invalid mode. Choose 'kinematic' or 'dynamic'.")

def atwood(rho1, rho2):
    """
    Calculates the Atwood number (A), a dimensionless density ratio used to 
    characterize density stratification and hydrodynamic instabilities.

    Formula:
        A = (rho1 - rho2) / (rho1 + rho2)

    Parameters:
        rho1 : float or array-like
            Density of the heavier fluid (kg/m³)
        rho2 : float or array-like
            Density of the lighter fluid (kg/m³)

    Returns:
        A : float or ndarray
            Atwood number (dimensionless). Propagates np.nan if any input is np.nan.
    """
    rho1, rho2 = validate_inputs(rho1, rho2)
    numerator = rho1 - rho2
    denominator = rho1 + rho2
    return safe_divide(numerator, denominator)

def bagnold(rho, d, gamma_dot, *, mode="lambda", mu=None, lambda_=None, phi=None, phi0=None):
    """
    Calculates the Bagnold number (Ba), a dimensionless number characterizing 
    the ratio of grain-inertia to viscous forces in granular flows.

    Modes:
        - 'lambda': 
            Ba = (rho * d² * sqrt(lambda) * γ̇) / μ
        - 'concentration': 
            Computes lambda using:
                lambda = 1 / ((phi0 / phi)^(1/3) - 1)
            Then applies:
                Ba = (rho * d² * sqrt(lambda) * γ̇) / μ

    Parameters:
        rho : float or array-like
            Particle density (kg/m³)
        d : float or array-like
            Grain diameter (m)
        gamma_dot : float or array-like
            Shear rate (1/s)
        mode : str, optional (default: 'lambda')
            Calculation mode: 'lambda' or 'concentration'
        mu : float or array-like
            Dynamic viscosity of the fluid (Pa·s), required in all modes
        lambda_ : float or array-like, required for 'lambda' mode
            Linear concentration parameter (dimensionless)
        phi : float or array-like, required for 'concentration' mode
            Solids fraction (volume fraction)
        phi0 : float or array-like, required for 'concentration' mode
            Maximum packing concentration (volume fraction)

    Returns:
        Ba : float or ndarray
            Bagnold number (dimensionless). Propagates np.nan if any input is np.nan.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    rho, d, gamma_dot = validate_inputs(rho, d, gamma_dot)

    if mu is None:
        raise ValueError("Dynamic viscosity 'mu' must be provided")
    mu, = validate_inputs(mu)

    if mode == "lambda":
        if lambda_ is None:
            raise ValueError("'lambda_' must be provided for mode='lambda'")
        lambda_, = validate_inputs(lambda_)

    elif mode == "concentration":
        if phi is None or phi0 is None:
            raise ValueError("Both 'phi' and 'phi0' must be provided for mode='concentration'")
        phi, phi0 = validate_inputs(phi, phi0)
        ratio = safe_divide(phi0, phi)
        root_term = np.cbrt(ratio)
        denominator = root_term - 1
        lambda_ = safe_divide(1, denominator)
    else:
        raise ValueError("Invalid mode. Choose 'lambda' or 'concentration'.")

    term = rho * d**2 * np.sqrt(lambda_) * gamma_dot
    return safe_divide(term, mu)

def bejan(
    *,
    mode,
    # For mode 1 (entropy ratio)
    sgen_deltaT=None,  # Entropy generation by heat transfer (W/K)
    sgen_deltap=None,  # Entropy generation by fluid friction (W/K)
    # For mode 2 (Brinkman)
    brinkman=None,     # Brinkman number (dimensionless)
    # For modes 3,4,5 (pressure drop modes)
    delta_p=None,      # Pressure drop (Pa)
    L=None,            # Characteristic length (m)
    mu=None,           # Dynamic viscosity (Pa·s)
    alpha=None,        # Thermal diffusivity (m²/s), mode 3 only
    D=None,            # Mass diffusivity (m²/s), mode 4 only
    nu=None,           # Kinematic viscosity (m²/s), mode 5 only
    # For mode 6 (Hagen-Poiseuille)
    Re=None,           # Reynolds number (dimensionless)
    d=None,            # Pipe diameter (m)
    # For modes 7 and 8 (exergy dissipation)
    Aw=None,           # Wet area (m²)
    rho=None,          # Density (kg/m³)
    u=None,            # Velocity (m/s)
    delta_X=None,      # Exergy dissipation rate difference (W)
    delta_S=None,      # Entropy dissipation rate difference (W/K)
    T0=None,           # Reference temperature (K), mode 8 only
):
    """
    Calculate the Bejan number based on selected mode.

    Modes:
    1. Entropy generation ratio
       Be = sgen_deltaT / (sgen_deltaT + sgen_deltap)

    2. Brinkman relation
       Be = 1 / (1 + brinkman)

    3. Heat transfer mode
       Be = (delta_p * L^2) / (mu * alpha)

    4. Mass transfer mode
       Be = (delta_p * L^2) / (mu * D)

    5. Fluid mechanics mode
       Be = (delta_p * L^2) / (mu * nu)

    6. Hagen-Poiseuille flow
       Be = (32 * Re * L^3) / (d^3)

    7. Exergy dissipation (exergy form)
       Be = (1 / (Aw * rho * u)) * (L^2 / nu^2) * delta_X

    8. Exergy dissipation (entropy form)
       Be = (1 / (Aw * rho * u)) * (T0 * L^2 / nu^2) * delta_S

    Parameters:
        mode : int
            Mode selector (1 to 8).
        sgen_deltaT : float or array-like, optional
            Entropy generation rate by heat transfer (W/K), required for mode 1.
        sgen_deltap : float or array-like, optional
            Entropy generation rate by fluid friction (W/K), required for mode 1.
        brinkman : float or array-like, optional
            Brinkman number (dimensionless), required for mode 2.
        delta_p : float or array-like, optional
            Pressure drop (Pa), required for modes 3,4,5.
        L : float or array-like, optional
            Characteristic length (m), required for modes 3,4,5,6,7,8.
        mu : float or array-like, optional
            Dynamic viscosity (Pa·s), required for modes 3,4,5.
        alpha : float or array-like, optional
            Thermal diffusivity (m²/s), required for mode 3.
        D : float or array-like, optional
            Mass diffusivity (m²/s), required for mode 4.
        nu : float or array-like, optional
            Kinematic viscosity (m²/s), required for modes 5,7,8.
        Re : float or array-like, optional
            Reynolds number (dimensionless), required for mode 6.
        d : float or array-like, optional
            Pipe diameter (m), required for mode 6.
        Aw : float or array-like, optional
            Wet area (m²), required for modes 7,8.
        rho : float or array-like, optional
            Density (kg/m³), required for modes 7,8.
        u : float or array-like, optional
            Velocity (m/s), required for modes 7,8.
        delta_X : float or array-like, optional
            Exergy dissipation rate difference (W), required for mode 7.
        delta_S : float or array-like, optional
            Entropy dissipation rate difference (W/K), required for mode 8.
        T0 : float or array-like, optional
            Reference temperature (K), required for mode 8.

    Returns:
        float or ndarray:
            Calculated Bejan number(s). np.nan propagates if present in inputs.

    Raises:
        ValueError if required parameters for the selected mode are missing or invalid mode.
    """

    # Assume validate_inputs and safe_divide are defined externally

    if mode == 1:
        if sgen_deltaT is None or sgen_deltap is None:
            raise ValueError("sgen_deltaT and sgen_deltap must be provided for mode 1")
        sgen_deltaT, sgen_deltap = validate_inputs(sgen_deltaT, sgen_deltap)
        numerator = sgen_deltaT
        denominator = sgen_deltaT + sgen_deltap
        return safe_divide(numerator, denominator)

    elif mode == 2:
        if brinkman is None:
            raise ValueError("brinkman must be provided for mode 2")
        brinkman, = validate_inputs(brinkman)
        return safe_divide(1, 1 + brinkman)

    elif mode == 3:
        if any(x is None for x in (delta_p, L, mu, alpha)):
            raise ValueError("delta_p, L, mu, and alpha must be provided for mode 3")
        delta_p, L, mu, alpha = validate_inputs(delta_p, L, mu, alpha)
        numerator = delta_p * L**2
        denominator = mu * alpha
        return safe_divide(numerator, denominator)

    elif mode == 4:
        if any(x is None for x in (delta_p, L, mu, D)):
            raise ValueError("delta_p, L, mu, and D must be provided for mode 4")
        delta_p, L, mu, D = validate_inputs(delta_p, L, mu, D)
        numerator = delta_p * L**2
        denominator = mu * D
        return safe_divide(numerator, denominator)

    elif mode == 5:
        if any(x is None for x in (delta_p, L, mu, nu)):

            raise ValueError("delta_p, L, mu, and nu must be provided for mode 5")
        delta_p, L, mu, nu = validate_inputs(delta_p, L, mu, nu)
        numerator = delta_p * L**2
        denominator = mu * nu
        return safe_divide(numerator, denominator)

    elif mode == 6:
        if any(x is None for x in (Re, L, d)):

            raise ValueError("Re, L, and d must be provided for mode 6")
        Re, L, d = validate_inputs(Re, L, d)
        numerator = 32 * Re * L**3
        denominator = d**3
        return safe_divide(numerator, denominator)

    elif mode == 7:
        if any(x is None for x in (Aw, rho, u, L, nu, delta_X)):

            raise ValueError("Aw, rho, u, L, nu, and delta_X must be provided for mode 7")
        Aw, rho, u, L, nu, delta_X = validate_inputs(Aw, rho, u, L, nu, delta_X)
        numerator = L**2 * delta_X
        denominator = Aw * rho * u * nu**2
        return safe_divide(numerator, denominator)

    elif mode == 8:
        if any(x is None for x in (Aw, rho, u, L, nu, T0, delta_S)):

            raise ValueError("Aw, rho, u, L, nu, T0, and delta_S must be provided for mode 8")
        Aw, rho, u, L, nu, T0, delta_S = validate_inputs(Aw, rho, u, L, nu, T0, delta_S)
        numerator = T0 * L**2 * delta_S
        denominator = Aw * rho * u * nu**2
        return safe_divide(numerator, denominator)

    else:
        raise ValueError(f"Invalid mode '{mode}'. Valid modes are 1 to 8.")

def bingham(tau_y, L, mu, V):
    """
    Calculates the Bingham number (Bm), a dimensionless number in rheology representing the ratio
    of yield stress to viscous stress.

    Bm = (tau_y * L) / (mu * V)

    Parameters:
        tau_y : float or array-like
            Yield stress (Pa)
        L : float or array-like
            Characteristic length (m)
        mu : float or array-like
            Dynamic viscosity (Pa·s)
        V : float or array-like
            Characteristic velocity (m/s)

    Returns:
        Bm : float or ndarray
            Bingham number, with np.nan propagated.

    Raises:
        ValueError: if any required parameter is missing
    """
    tau_y, L, mu, V = validate_inputs(tau_y, L, mu, V)
    if any(x is None for x in (tau_y, L, mu, V)):
        raise ValueError("All parameters tau_y, L, mu, V must be provided.")

    return safe_divide(tau_y * L, mu * V)

def blake(u, rho, Dh, mu, epsilon):
    """
    Calculates the Blake number (B), a dimensionless number used in fluid mechanics
    to characterize flow in porous media.

    B = (u * rho * Dh) / (mu * (1 - epsilon))

    Parameters:
        u : float or array-like
            Flow velocity (m/s)
        rho : float or array-like
            Fluid density (kg/m³)
        Dh : float or array-like
            Hydraulic diameter (m)
        mu : float or array-like
            Dynamic viscosity (Pa·s)
        epsilon : float or array-like
            Void fraction (dimensionless, 0 < epsilon < 1)

    Returns:
        B : float or ndarray
            Blake number, with np.nan propagated.

    Raises:
        ValueError: if any required parameter is missing or if epsilon values are invalid
    """
    u, rho, Dh, mu, epsilon = validate_inputs(u, rho, Dh, mu, epsilon)

    # Check for valid epsilon values (avoid division by zero or negative)
    if np.any((epsilon >= 1) | (epsilon < 0)):
        raise ValueError("Void fraction 'epsilon' must be in the range [0, 1).")

    numerator = u * rho * Dh
    denominator = mu * (1 - epsilon)
    return safe_divide(numerator, denominator)

def bond(*, mode=1, delta_rho=None, g=None, L=None, gamma=None,  
         capillary_length=None, M=None, contact_length=None):
    """
    Calculate the Bond number (Bo), also known as the Eötvös number, which expresses the ratio
    of gravitational forces to surface tension forces.

    Modes:
    1. Direct calculation:
       Bo = (delta_rho * g * L^2) / gamma

    2. Using capillary length:
       Bo = (L / capillary_length)^2
       where capillary_length = sqrt(gamma / (rho * g))

    3. Using mass, gravity, surface tension, and contact length:
       Bo = (M * g) / (gamma * contact_length)

    Parameters:
    - delta_rho: Difference in density between two phases (kg/m^3)
    - g: Gravitational acceleration (m/s^2)
    - L: Characteristic length (m)
    - gamma: Surface tension (N/m)
    - capillary_length: Capillary length (m)
    - M: Mass of the object (kg)
    - contact_length: Contact perimeter length (m)

    Returns:
    - Bond number (dimensionless)
    """

    if mode == 1:
        if any(x is None for x in (delta_rho, g, L, gamma)):
            raise ValueError("Mode 1 requires delta_rho, g, L, and gamma.")
        delta_rho, g, L, gamma = map(np.asarray, (delta_rho, g, L, gamma))
        numerator = delta_rho * g * L**2
        return safe_divide(numerator, gamma)

    elif mode == 2:
        if any(x is None for x in (L, capillary_length)):
            raise ValueError("Mode 2 requires L and capillary_length.")
        L, capillary_length = map(np.asarray, (L, capillary_length))
        return (L / capillary_length)**2

    elif mode == 3:
        if any(x is None for x in (M, g, gamma, contact_length)):
            raise ValueError("Mode 3 requires M, g, gamma, and contact_length.")
        M, g, gamma, contact_length = map(np.asarray, (M, g, gamma, contact_length))
        numerator = M * g
        denominator = gamma * contact_length
        return safe_divide(numerator, denominator)

    else:
        raise ValueError("Invalid mode selected. Choose mode 1, 2, or 3.")

def brinkman(*, mode="full", mu=None, u=None, kappa=None, Tw=None, T0=None, Pr=None, Ec=None):
    """
    Calculate the Brinkman number (Br), a dimensionless quantity representing the ratio of
    viscous dissipation to thermal conduction in fluid flow.

    Modes:
    1. Full definition:
       Br = (μ * u²) / [κ * (Tw - T0)]

    2. Reduced form:
       Br = Pr * Ec

    Parameters:
    - mode: Calculation mode, either 'full' or 'reduced' (default: 'full')

    For mode='full':
    - mu: Dynamic viscosity μ (Pa·s)
    - u: Flow velocity u (m/s)
    - kappa: Thermal conductivity κ (W/m·K)
    - Tw: Wall temperature (K)
    - T0: Bulk fluid temperature (K)

    For mode='reduced':
    - Pr: Prandtl number (dimensionless)
    - Ec: Eckert number (dimensionless)

    Returns:
    - Brinkman number (dimensionless), as a float or ndarray with np.nan propagated
    """

    if mode == "full":
        if any(x is None for x in (mu, u, kappa, Tw, T0)):
            raise ValueError("Parameters 'mu', 'u', 'kappa', 'Tw', and 'T0' are required for mode='full'")
        mu, u, kappa, Tw, T0 = validate_inputs(mu, u, kappa, Tw, T0)
        delta_T = Tw - T0
        numerator = mu * u * u
        denominator = kappa * delta_T
        return safe_divide(numerator, denominator)

    elif mode == "reduced":
        if Pr is None or Ec is None:
            raise ValueError("Parameters 'Pr' and 'Ec' are required for mode='reduced'")
        Pr, Ec = validate_inputs(Pr, Ec)
        return Pr * Ec

    else:
        raise ValueError("Invalid mode. Choose 'full' or 'reduced'.")

def burger(*, mode="dimensionless", Ro=None, Fr=None, g=None, H=None, f=None, L=None):
    """
    Calculate the Burger number (Bu), a dimensionless quantity representing the ratio of
    rotational to gravitational effects in geophysical flows.

    Modes:
    1. Dimensionless form:
       Bu = (Ro / Fr)^2

    2. Components form:
       Bu = (sqrt(g * H) / (f * L))^2

    Parameters:
    - mode: Calculation mode, either 'dimensionless' or 'components' (default: 'dimensionless')

    For mode='dimensionless':
    - Ro: Rossby number (dimensionless)
    - Fr: Froude number (dimensionless)

    For mode='components':
    - g: Gravitational acceleration (m/s^2)
    - H: Characteristic depth or height (m)
    - f: Coriolis parameter (1/s)
    - L: Characteristic horizontal length (m)

    Returns:
    - Burger number (dimensionless), as a float or ndarray with np.nan propagated
    """
    if mode == "dimensionless":
        if Ro is None or Fr is None:
            raise ValueError("Parameters 'Ro' and 'Fr' are required for mode='dimensionless'")
        Ro, Fr = validate_inputs(Ro, Fr)
        return safe_divide(Ro, Fr) ** 2

    elif mode == "components":
        if any(x is None for x in (g, H, f, L)):
            raise ValueError("Parameters 'g', 'H', 'f', and 'L' are required for mode='components'")
        g, H, f, L = validate_inputs(g, H, f, L)
        numerator = np.sqrt(g * H)
        denominator = f * L
        return safe_divide(numerator, denominator) ** 2

    else:
        raise ValueError("Invalid mode. Choose 'dimensionless' or 'components'.")

def biot(*, mode="standard",
         h=None, k=None, L=None,
         sigma=None, T=None,  # for radiative
         kc=None, D=None      # for mass transfer
         ):
    """
    Calculate Biot number in different modes.

    Supported modes:
        - 'standard':      Bi = (h * L) / k
        - 'reciprocal':    Bi = k / (h * L)
        - 'radiative':     Bi = (sigma * T^3 * L) / k
        - 'mass':          Bi = (kc / D) * L

    Parameters
    ----------
    mode : str
        One of 'standard', 'reciprocal', 'radiative', or 'mass'.
    
    h : float or array-like, optional
        Convective heat transfer coefficient [W/(m²·K)] (used in 'standard').
    
    k : float or array-like, optional
        Thermal conductivity [W/(m·K)] (used in 'standard', 'reciprocal', 'radiative').
    
    L : float or array-like, optional
        Characteristic length [m] (used in all modes).

    sigma : float or array-like, optional
        Stefan-Boltzmann constant [W/(m²·K⁴)] (used in 'radiative').

    T : float or array-like, optional
        Temperature [K] (used in 'radiative').

    kc : float or array-like, optional
        Convective mass transfer coefficient [m/s] (used in 'mass').

    D : float or array-like, optional
        Mass diffusivity [m²/s] (used in 'mass').

    Returns
    -------
    Bi : float or np.ndarray
        Calculated Biot number(s), with NaNs propagated.

    Raises
    ------
    ValueError
        If the mode is not recognized or required parameters are missing.
    """

    mode = mode.lower()
    
    if mode == 'standard':
        if h is None or k is None or L is None:
            raise ValueError("For 'standard' mode, h, k, and L must be provided.")
        h, k, L = validate_inputs(h, k, L)
        Bi = safe_divide(h * L, k) 

    elif mode == 'reciprocal':
        if h is None or k is None or L is None:
            raise ValueError("For 'reciprocal' mode, h, k, and L must be provided.")
        h, k, L = validate_inputs(h, k, L)
        Bi = safe_divide(k, h * L) 

    elif mode == 'radiative':
        if sigma is None or T is None or k is None or L is None:
            raise ValueError("For 'radiative' mode, sigma, T, k, and L must be provided.")
        sigma, T, k, L = validate_inputs(sigma, T, k, L)
        Bi = safe_divide(sigma * T**3 * L, k)

    elif mode == 'mass':
        if kc is None or D is None or L is None:
            raise ValueError("For 'mass' mode, kc, D, and L must be provided.")
        kc, D, L = validate_inputs(kc, D, L)
        Bi = safe_divide(kc * L, D)

    else:
        raise ValueError("Mode must be one of 'standard', 'reciprocal', 'radiative', or 'mass'.")

    return Bi

def brownell_katz(u, mu, krw, sigma):
    """
    Calculate the Brownell–Katz number (NBK), a dimensionless quantity that characterizes
    the relative effects of viscous and capillary forces in porous media flow.

    Formula:
        NBK = (u * mu) / (krw * sigma)

    Parameters:
    - u: Flow velocity (m/s)
    - mu: Dynamic viscosity (Pa·s)
    - krw: Relative permeability to water (dimensionless)
    - sigma: Interfacial tension or surface tension (N/m)

    Returns:
    - Brownell–Katz number (dimensionless), as a float or ndarray with np.nan propagated
    """
    if any(x is None for x in (u, mu, krw, sigma)):
        raise ValueError("Parameters 'u', 'mu', 'krw', and 'sigma' must all be provided.")

    u, mu, krw, sigma = validate_inputs(u, mu, krw, sigma)
    numerator = u * mu
    denominator = krw * sigma
    return safe_divide(numerator, denominator)

def capillary(mu, V, sigma):
    """
    Calculate the Capillary number (Ca), a dimensionless quantity representing the ratio
    of viscous forces to surface tension forces in multiphase flow.

    Formula:
        Ca = (mu * V) / sigma

    Parameters:
    - mu: Dynamic viscosity of the liquid (Pa·s)
    - V: Characteristic velocity (m/s)
    - sigma: Surface or interfacial tension (N/m)

    Returns:
    - Capillary number (dimensionless), as a float or ndarray with np.nan propagated
    """
    if any(x is None for x in (mu, V, sigma)):
        raise ValueError("Parameters 'mu', 'V', and 'sigma' must all be provided.")

    mu, V, sigma = validate_inputs(mu, V, sigma)
    numerator = mu * V
    return safe_divide(numerator, sigma)

def cavitation(p, pv, rho, v):
    """
    Calculate the Cavitation number (Ca), a dimensionless number representing the ratio of
    pressure difference to the dynamic pressure in a flowing fluid.

    Formula:
        Ca = (p - pv) / (0.5 * rho * v^2)

    Parameters:
    - p: Local pressure (Pa)
    - pv: Vapor pressure of the fluid (Pa)
    - rho: Fluid density (kg/m^3)
    - v: Characteristic velocity of the flow (m/s)

    Returns:
    - Cavitation number (dimensionless), scalar or ndarray with np.nan propagated
    """
    if any(x is None for x in (p, pv, rho, v)):
        raise ValueError("Parameters 'p', 'pv', 'rho', and 'v' must all be provided.")

    p, pv, rho, v = validate_inputs(p, pv, rho, v)
    numerator = p - pv
    denominator = 0.5 * rho * v**2
    return safe_divide(numerator, denominator)

def chandrasekhar(*, mode="mode1", B0=None, d=None, mu0=None, rho=None, nu=None, lambda_=None,
                  B=None, L=None, mu=None, Dm=None, Ha=None):
    """
    Calculates the Chandrasekhar number (C) in one of three modes.

    Mode 1 (classic):
        C = (B0^2 * d^2) / (mu0 * rho * nu * lambda)

    Mode 2 (magnetic diffusivity form):
        C = (B^2 * L^2) / (mu0 * mu * Dm)

    Mode 3 (from Hartmann number):
        C = Ha^2

    Parameters:
        mode : str, optional (default: 'mode1')
            Calculation mode: 'mode1', 'mode2', or 'mode3'

        Mode 1 parameters:
            B0 : float or array-like
                Characteristic magnetic field (T)
            d : float or array-like
                Characteristic length (m)
            mu0 : float or array-like
                Magnetic permeability (H/m)
            rho : float or array-like
                Fluid density (kg/m^3)
            nu : float or array-like
                Kinematic viscosity (m^2/s)
            lambda_ : float or array-like
                Magnetic diffusivity (m^2/s)

        Mode 2 parameters:
            B : float or array-like
                Magnetic field (T)
            L : float or array-like
                Characteristic length (m)
            mu : float or array-like
                Magnetic permeability (relative or absolute)
            Dm : float or array-like
                Magnetic diffusivity

        Mode 3 parameter:
            Ha : float or array-like
                Hartmann number (dimensionless)

    Returns:
        C : float or ndarray
            Chandrasekhar number, with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    if mode == "mode1":
        if None in (B0, d, mu0, rho, nu, lambda_):
            raise ValueError("Mode 1 requires B0, d, mu0, rho, nu, and lambda_")
        B0, d, mu0, rho, nu, lambda_ = validate_inputs(B0, d, mu0, rho, nu, lambda_)
        numerator = B0**2 * d**2
        denominator = mu0 * rho * nu * lambda_
        return safe_divide(numerator, denominator)

    elif mode == "mode2":
        if None in (B, L, mu0, mu, Dm):
            raise ValueError("Mode 2 requires B, L, mu0, mu, and Dm")
        B, L, mu0, mu, Dm = validate_inputs(B, L, mu0, mu, Dm)
        numerator = B**2 * L**2
        denominator = mu0 * mu * Dm
        return safe_divide(numerator, denominator)

    elif mode == "mode3":
        if Ha is None:
            raise ValueError("Mode 3 requires Ha")
        Ha, = validate_inputs(Ha)
        return Ha**2

    else:
        raise ValueError("Invalid mode. Choose 'mode1', 'mode2', or 'mode3'.")

def chilton_colburn(*, mode="Mode 1", Nu=None, Re=None, Pr=None,
                    Sh=None, Sc=None, h=None, cp=None, G=None,
                    kc=None, v=None, f=None):
    """
    Calculates the Chilton–Colburn j-factor (J) using one of five modes.

    Modes and Formulas:
        Mode 1: J = Nu / (Re * Pr^(1/3))
        Mode 2: J = Sh / (Re * Sc^(1/3))
        Mode 3: J = (h / (cp * G)) * Pr^(2/3)
        Mode 4: J = (kc / v) * Sc^(2/3)
        Mode 5: J = f / 2

    Parameters:
        mode : str, optional (default: 'Mode 1')
            Calculation mode: 'Mode 1', 'Mode 2', 'Mode 3', 'Mode 4', or 'Mode 5'

        Mode 1 parameters:
            Nu : float or array-like
                Nusselt number
            Re : float or array-like
                Reynolds number
            Pr : float or array-like
                Prandtl number

        Mode 2 parameters:
            Sh : float or array-like
                Sherwood number
            Re : float or array-like
                Reynolds number
            Sc : float or array-like
                Schmidt number

        Mode 3 parameters:
            h : float or array-like
                Convective heat transfer coefficient (W/m²·K)
            cp : float or array-like
                Specific heat capacity (J/kg·K)
            G : float or array-like
                Mass flux (kg/m²·s)
            Pr : float or array-like
                Prandtl number

        Mode 4 parameters:
            kc : float or array-like
                Mass transfer coefficient (m/s)
            v : float or array-like
                Average velocity (m/s)
            Sc : float or array-like
                Schmidt number

        Mode 5 parameters:
            f : float or array-like
                Friction factor (dimensionless)

    Returns:
        J : float or ndarray
            Chilton–Colburn j-factor, with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    if mode == "Mode 1":
        if None in (Nu, Re, Pr):
            raise ValueError("Mode 1 requires Nu, Re, and Pr")
        Nu, Re, Pr = validate_inputs(Nu, Re, Pr)
        return safe_divide(Nu, Re * Pr**(1/3))

    elif mode == "Mode 2":
        if None in (Sh, Re, Sc):
            raise ValueError("Mode 2 requires Sh, Re, and Sc")
        Sh, Re, Sc = validate_inputs(Sh, Re, Sc)
        return safe_divide(Sh, Re * Sc**(1/3))

    elif mode == "Mode 3":
        if None in (h, cp, G, Pr):
            raise ValueError("Mode 3 requires h, cp, G, and Pr")
        h, cp, G, Pr = validate_inputs(h, cp, G, Pr)
        return safe_divide(h, cp * G) * Pr**(2/3)

    elif mode == "Mode 4":
        if None in (kc, v, Sc):
            raise ValueError("Mode 4 requires kc, v, and Sc")
        kc, v, Sc = validate_inputs(kc, v, Sc)
        return safe_divide(kc, v) * Sc**(2/3)

    elif mode == "Mode 5":
        if f is None:
            raise ValueError("Mode 5 requires f")
        f, = validate_inputs(f)
        return safe_divide(f, 2)

    else:
        raise ValueError("Invalid mode. Choose 'Mode 1', 'Mode 2', 'Mode 3', 'Mode 4', or 'Mode 5'.")

def damkohler(*, mode="Mode 1", k=None, C0=None, n=None, tau=None,
              Q=None, cp=None, dT=None, kg=None, a=None):
    """
    Calculates the Damköhler number (Da) using one of three modes.

    Modes and Formulas:
        Mode 1: Da = k * C0^(n-1) * tau
        Mode 2: Da = (k * Q) / (cp * ΔT)
        Mode 3: Da = k * C0^(n-1) / (kg * a)

    Parameters:
        mode : str, optional (default: 'Mode 1')
            Calculation mode: 'Mode 1', 'Mode 2', or 'Mode 3'

        Mode 1 parameters:
            k : float or array-like
                Reaction rate constant
            C0 : float or array-like
                Initial concentration
            n : float or array-like
                Reaction order
            tau : float or array-like
                Mean residence time

        Mode 2 parameters:
            k : float or array-like
                Reaction rate constant
            Q : float or array-like
                Process flow rate (energy or mass)
            cp : float or array-like
                Specific heat capacity
            dT : float or array-like
                Temperature difference (ΔT)

        Mode 3 parameters:
            k : float or array-like
                Reaction rate constant
            C0 : float or array-like
                Initial concentration
            n : float or array-like
                Reaction order
            kg : float or array-like
                Global mass transport coefficient
            a : float or array-like
                Interfacial area

    Returns:
        Da : float or ndarray
            Damköhler number, with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    if mode == "Mode 1":
        if None in (k, C0, n, tau):
            raise ValueError("Mode 1 requires k, C0, n, and tau")
        k, C0, n, tau = validate_inputs(k, C0, n, tau)
        return k * C0**(n - 1) * tau

    elif mode == "Mode 2":
        if None in (k, Q, cp, dT):
            raise ValueError("Mode 2 requires k, Q, cp, and dT")
        k, Q, cp, dT = validate_inputs(k, Q, cp, dT)
        return safe_divide(k * Q, cp * dT)

    elif mode == "Mode 3":
        if None in (k, C0, n, kg, a):
            raise ValueError("Mode 3 requires k, C0, n, kg, and a")
        k, C0, n, kg, a = validate_inputs(k, C0, n, kg, a)
        return safe_divide(k * C0**(n - 1), kg * a)

    else:
        raise ValueError("Invalid mode. Choose 'Mode 1', 'Mode 2', or 'Mode 3'.")

def darcy_friction_factor(
    *,
    mode,
    delta_p_per_L=None,
    rho=None,
    v=None,
    D=None,
    S=None,
    g=9.81,
    Q=None,
    D_c=None,
    tau=None,
    R_star=None,
    Re=None,
    epsilon=None
):
    """
    Calculates the Darcy friction factor f using one of five modes based on available flow and pipe parameters.

    Equations for friction factor f solved explicitly and typical use cases:

    Mode 1: Pressure loss per unit length (Δp/L)
        f = (2 * D * Δp/L) / (ρ * v²)
        - Used when you know the pressure gradient along the pipe and want to find friction factor.
        - Common in experiments or simulations where pressure drop is directly measured.
        - Requires fluid density, velocity, hydraulic diameter, and pressure loss.

    Mode 2: Head loss per unit length (S = Δh/L)
        f = (2 * g * D * S) / v²
        - Uses head loss (height equivalent of pressure loss) instead of direct pressure.
        - Useful when energy loss is measured as a hydraulic head.
        - Requires velocity, hydraulic diameter, gravitational acceleration, and head loss.

    Mode 3: Head loss with volumetric flow rate and pipe diameter
        f = (π² * g * D_c⁵ * S) / (8 * Q²)
        - Suitable when volumetric flow rate is measured rather than velocity.
        - Useful for circular pipes where diameter and flow rate are known.
        - Requires head loss, pipe diameter, volumetric flow rate, and gravitational acceleration.

    Mode 4: Wall shear stress τ
        f = (8 * τ) / (ρ * v²)
        - Used when wall shear stress is known or measured directly.
        - Common in detailed fluid mechanics studies or CFD simulations.
        - Requires shear stress, fluid density, and velocity.

    Mode 5: Dimensionless roughness Reynolds number R_star
        f = (8 * R_star² * D²) / (Re² * ε²)
        - Applies in rough pipe flow characterization.
        - Connects friction factor to relative roughness and flow regime via Reynolds number.
        - Requires dimensionless roughness Reynolds number, pipe diameter, Reynolds number, and surface roughness.

    Parameters
    ----------
    mode : str
        Mode selection (case-insensitive):
        'mode1' - from pressure loss per unit length (Δp/L)
        'mode2' - from head loss per unit length (S = Δh/L)
        'mode3' - from head loss per unit length, volumetric flow rate, and pipe diameter
        'mode4' - from wall shear stress τ
        'mode5' - from dimensionless roughness Reynolds number R_star

    delta_p_per_L : float or array-like, required for mode1
        Pressure loss per unit length (Pa/m)

    rho : float or array-like, required for modes 1 and 4
        Fluid density (kg/m³)

    v : float or array-like, required for modes 1, 2, and 4
        Mean flow velocity (m/s)

    D : float or array-like, required for modes 1, 2, and 5
        Hydraulic diameter (m)

    S : float or array-like, required for modes 2 and 3
        Head loss per unit length (dimensionless m/m)

    g : float or array-like, optional, default 9.81
        Gravitational acceleration (m/s²)

    Q : float or array-like, required for mode3
        Volumetric flow rate (m³/s)

    D_c : float or array-like, required for mode3
        Pipe diameter (m)

    tau : float or array-like, required for mode4
        Wall shear stress (Pa)

    R_star : float or array-like, required for mode5
        Dimensionless roughness Reynolds number

    Re : float or array-like, required for mode5
        Reynolds number

    epsilon : float or array-like, required for mode5
        Surface roughness (m)

    Returns
    -------
    f : float or ndarray
        Darcy friction factor, with np.nan propagated

    Raises
    ------
    ValueError
        If required parameters for the selected mode are missing or invalid mode is selected.
    """
    mode = mode.lower()
    # Validate inputs helper (assumed provided)
    def validate_inputs(*args):
        # Convert all inputs to np.array of floats or np.nan if None
        validated = []
        for a in args:
            if a is None:
                validated.append(np.nan)
            else:
                validated.append(np.array(a, dtype=float))
        return tuple(validated)

    # Safe divide helper (assumed provided)
    def safe_divide(num, den):
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.true_divide(num, den)
            result = np.where(np.isnan(num) | np.isnan(den), np.nan, result)
        return result

    if mode == "mode1":
        if delta_p_per_L is None or rho is None or v is None or D is None:
            raise ValueError("For mode1, delta_p_per_L, rho, v, and D must be provided")
        delta_p_per_L, rho, v, D = validate_inputs(delta_p_per_L, rho, v, D)
        numerator = 2 * D * delta_p_per_L
        denominator = rho * v ** 2
        return safe_divide(numerator, denominator)

    elif mode == "mode2":
        if S is None or v is None or D is None:
            raise ValueError("For mode2, S, v, and D must be provided")
        S, v, D = validate_inputs(S, v, D)
        g_arr = np.full_like(S, g, dtype=float) if np.isscalar(g) else np.array(g, dtype=float)
        numerator = 2 * g_arr * D * S
        denominator = v ** 2
        return safe_divide(numerator, denominator)

    elif mode == "mode3":
        if S is None or Q is None or D_c is None:
            raise ValueError("For mode3, S, Q, and D_c must be provided")
        S, Q, D_c = validate_inputs(S, Q, D_c)
        g_arr = np.full_like(S, g, dtype=float) if np.isscalar(g) else np.array(g, dtype=float)
        numerator = (np.pi ** 2) * g_arr * (D_c ** 5) * S
        denominator = 8 * (Q ** 2)
        return safe_divide(numerator, denominator)

    elif mode == "mode4":
        if tau is None or rho is None or v is None:
            raise ValueError("For mode4, tau, rho, and v must be provided")
        tau, rho, v = validate_inputs(tau, rho, v)
        numerator = 8 * tau
        denominator = rho * v ** 2
        return safe_divide(numerator, denominator)

    elif mode == "mode5":
        if R_star is None or D is None or Re is None or epsilon is None:
            raise ValueError("For mode5, R_star, D, Re, and epsilon must be provided")
        R_star, D, Re, epsilon = validate_inputs(R_star, D, Re, epsilon)
        numerator = 8 * (R_star ** 2) * (D ** 2)
        denominator = (Re ** 2) * (epsilon ** 2)
        return safe_divide(numerator, denominator)

    else:
        raise ValueError("Invalid mode. Choose 'mode1', 'mode2', 'mode3', 'mode4', or 'mode5'.")

def darcy(K, d):
    """
    Calculates the Darcy number (Da), which quantifies the relative permeability 
    of a porous medium with respect to a characteristic length scale.

    Darcy number is defined as:
        Da = K / d^2

    Parameters:
        K : float or array-like
            Permeability of the medium (m²)
        d : float or array-like
            Characteristic length, e.g., particle diameter (m)

    Returns:
        Da : float or ndarray
            Darcy number, with np.nan propagated.

    Notes:
        - Inputs can be scalars or arrays; broadcasting is supported.
        - If any input contains np.nan, the result will propagate np.nan accordingly.
    """
    K, d = validate_inputs(K, d)
    return safe_divide(K, d**2)

def dean(*, mode="mode 1", rho=None, D=None, v=None, mu=None, Rc=None, Re=None):
    """
    Calculates the Dean number (De) for flow in a curved pipe or channel.

    The Dean number is a dimensionless number expressing the ratio of inertial and centrifugal forces 
    to viscous forces. It characterizes flow in curved pipes and is important for secondary flow analysis.

    Two calculation modes are available:

    mode 1 (default):
        De = (rho * D * v / mu) * sqrt(D / (2 * Rc))
        Requires fluid density (rho), diameter (D), axial velocity (v), dynamic viscosity (mu), and radius of curvature (Rc).

    mode 2:
        De = Re * sqrt(D / (2 * Rc))
        Requires Reynolds number (Re), diameter (D), and radius of curvature (Rc).

    Parameters:
        mode : str, optional (default: "mode 1")
            Calculation mode: "mode 1" or "mode 2"
        rho : float or array-like, required for mode 1
            Fluid density (kg/m³)
        D : float or array-like, required
            Diameter (m)
        v : float or array-like, required for mode 1
            Axial velocity scale (m/s)
        mu : float or array-like, required for mode 1
            Dynamic viscosity (Pa·s)
        Rc : float or array-like, required
            Radius of curvature (m)
        Re : float or array-like, required for mode 2
            Reynolds number (dimensionless)

    Returns:
        De : float or ndarray
            Dean number, with np.nan propagated.

    Raises:
        ValueError: If required parameters for the chosen mode are missing or if mode is invalid.
    """
    if mode not in ("mode 1", "mode 2"):
        raise ValueError("Invalid mode. Choose 'mode 1' or 'mode 2'.")

    # Validate D and Rc for both modes
    D, Rc = validate_inputs(D, Rc)

    if mode == "mode 1":
        missing = [name for name, val in (("rho", rho), ("v", v), ("mu", mu)) if val is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'mode 1': {', '.join(missing)}")
        rho, v, mu = validate_inputs(rho, v, mu)

        # Compute sqrt term safely (propagate nan)
        with np.errstate(invalid='ignore'):
            curvature_term = np.sqrt(safe_divide(D, 2 * Rc))
        # Calculate Dean number
        numerator = rho * D * v
        denominator = mu
        de = safe_divide(numerator, denominator) * curvature_term

    else:  # mode == "mode 2"
        if Re is None:
            raise ValueError("Parameter 'Re' must be provided for mode='mode 2'.")
        Re, = validate_inputs(Re)

        with np.errstate(invalid='ignore'):
            curvature_term = np.sqrt(safe_divide(D, 2 * Rc))

        de = Re * curvature_term

    return de
    import numpy as np

    def run_tests():
        # Scalars mode 1
        de1 = dean(mode="mode 1", rho=1000, D=0.05, v=2, mu=0.001, Rc=0.1)
        print(f"Dean number (mode 1, scalar): {de1}")

        # Scalars mode 2
        de2 = dean(mode="mode 2", Re=10000, D=0.05, Rc=0.1)
        print(f"Dean number (mode 2, scalar): {de2}")

        # Vector inputs mode 1
        rho = np.array([1000, 998, 995])
        D = np.array([0.05, 0.05, 0.05])
        v = np.array([2, 2.5, 3])
        mu = np.array([0.001, 0.0009, 0.0011])
        Rc = np.array([0.1, 0.12, 0.11])
        de_vec1 = dean(mode="mode 1", rho=rho, D=D, v=v, mu=mu, Rc=Rc)
        print(f"Dean number (mode 1, vector): {de_vec1}")

        # Vector + scalar mixed inputs mode 2
        Re = np.array([5000, 7000, 9000])
        D = 0.05
        Rc = 0.1
        de_vec2 = dean(mode="mode 2", Re=Re, D=D, Rc=Rc)
        print(f"Dean number (mode 2, mixed vector/scalar): {de_vec2}")

        # nan propagation mode 1
        de_nan = dean(mode="mode 1", rho=np.nan, D=0.05, v=2, mu=0.001, Rc=0.1)
        print(f"Dean number (mode 1, with nan): {de_nan}")

        # nan propagation mode 2
        de_nan2 = dean(mode="mode 2", Re=np.array([10000, np.nan]), D=0.05, Rc=0.1)
        print(f"Dean number (mode 2, with nan in vector): {de_nan2}")

        # Test invalid mode raises error
        try:
            dean(mode="invalid_mode", rho=1000, D=0.05, v=2, mu=0.001, Rc=0.1)
        except ValueError as e:
            print(f"Caught expected error: {e}")

        # Test missing parameter error
        try:
            dean(mode="mode 1", rho=1000, D=0.05, v=2, Rc=0.1)
        except ValueError as e:
            print(f"Caught expected error: {e}")

    run_tests()

def deborah(tc, tp):
    """
    Calculates the Deborah number (De), defined as the ratio of the relaxation time to the process time scale.

    Deborah number is a dimensionless number that characterizes the fluidity of materials under specific flow conditions.

    Parameters:
        tc : float or array-like
            Relaxation time (s)
        tp : float or array-like
            Process or observation time scale (s)

    Returns:
        De : float or ndarray
            Deborah number, with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or invalid.
    """
    tc, tp = validate_inputs(tc, tp)
    return safe_divide(tc, tp)

def drag_coefficient(*, mode="force", Fd=None, rho=None, u=None, A=None, tau=None):
    """
    Calculates the drag coefficient (cd) using one of two modes:

    Mode "force" (default):
        cd = 2 * Fd / (rho * u^2 * A)
        where Fd is the drag force,
              rho is fluid density,
              u is flow speed relative to fluid,
              A is reference area.

    Mode "stress":
        cd = tau / q = 2 * tau / (rho * u^2)
        where tau is local shear stress,
              rho is fluid density,
              u is local flow speed,
              q is local dynamic pressure = 0.5 * rho * u^2.

    Parameters:
        mode : str, optional (default "force")
            Calculation mode: "force" or "stress".
        Fd : float or array-like, required for mode "force"
            Drag force (N).
        rho : float or array-like, required for both modes
            Fluid density (kg/m³).
        u : float or array-like, required for both modes
            Flow speed relative to fluid (m/s).
        A : float or array-like, required for mode "force"
            Reference area (m²).
        tau : float or array-like, required for mode "stress"
            Local shear stress (Pa).

    Returns:
        cd : float or ndarray
            Drag coefficient with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid.
    """
    mode = mode.lower()
    if mode not in ("force", "stress"):
        raise ValueError("Invalid mode. Choose 'force' or 'stress'.")

    rho, u = validate_inputs(rho, u)

    if mode == "force":
        missing = [name for name, val in (("Fd", Fd), ("A", A)) if val is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'force': {', '.join(missing)}")
        Fd, A = validate_inputs(Fd, A)
        denominator = rho * u**2 * A
        return safe_divide(2 * Fd, denominator)

    else:  # mode == "stress"
        if tau is None:
            raise ValueError("Parameter 'tau' must be provided for mode='stress'.")
        tau, = validate_inputs(tau)
        denominator = rho * u**2
        return safe_divide(2 * tau, denominator)

def dukhin(
    *,
    mode="mode 1",
    kappa_sigma=None,
    Km=None,
    a=None,
    m=None,
    kappa=None,
    z=None,
    F=None,
    zeta=None,
    R=None,
    T=None,
    epsilon0=None,
    epsilonm=None,
    eta=None,
    D=None,
):
    """
    Calculates the Dukhin number (Du) using one of three modes.

    Modes:
        mode 1:
            Du = kappa_sigma / (Km * a)
            where
                kappa_sigma : surface conductivity
                Km : bulk fluid conductivity
                a : particle size

        mode 2:
            Du = 2 * (1 + 3m / z^2) * kappa * a * (cosh(z * F * zeta / (2 * R * T)) - 1)
            where
                m : electro-osmosis contribution parameter
                kappa : surface conductivity (different from kappa_sigma)
                a : particle size
                z : ion valency
                F : Faraday constant
                zeta : electrokinetic potential
                R : gas constant
                T : absolute temperature

        mode 3:
            Same as mode 2 but calculates m internally as:
                m = (2 * epsilon0 * epsilonm * R^2 * T^2) / (3 * eta * F^2 * D)
            Requires:
                epsilon0 : vacuum permittivity
                epsilonm : fluid permittivity
                eta : dynamic viscosity
                D : diffusion coefficient
                plus all mode 2 parameters except m

    Parameters:
        mode : str, optional (default "mode 1")
            Calculation mode: "mode 1", "mode 2", or "mode 3".
        kappa_sigma : float or array-like
            Surface conductivity (required for mode 1).
        Km : float or array-like
            Bulk conductivity (required for mode 1).
        a : float or array-like
            Particle size (required for all modes).
        m : float or array-like
            Electro-osmosis parameter (required for mode 2).
        kappa : float or array-like
            Surface conductivity (required for mode 2 and 3).
        z : float or array-like
            Ion valency (required for mode 2 and 3).
        F : float or array-like
            Faraday constant (required for mode 2 and 3).
        zeta : float or array-like
            Electrokinetic potential (required for mode 2 and 3).
        R : float or array-like
            Gas constant (required for mode 2 and 3).
        T : float or array-like
            Absolute temperature (required for mode 2 and 3).
        epsilon0 : float or array-like
            Vacuum permittivity (required for mode 3).
        epsilonm : float or array-like
            Fluid permittivity (required for mode 3).
        eta : float or array-like
            Dynamic viscosity (required for mode 3).
        D : float or array-like
            Diffusion coefficient (required for mode 3).

    Returns:
        Du : float or ndarray
            Dukhin number with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid.
    """

    mode = mode.lower()
    valid_modes = {"mode 1", "mode 2", "mode 3"}
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode. Choose from {valid_modes}.")

    def _check_missing(params):
        missing = [name for name, val in params if val is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for {mode}: {', '.join(missing)}")

    if mode == "mode 1":
        _check_missing([("kappa_sigma", kappa_sigma), ("Km", Km), ("a", a)])
        kappa_sigma, Km, a = validate_inputs(kappa_sigma, Km, a)
        denominator = Km * a
        return safe_divide(kappa_sigma, denominator)

    elif mode == "mode 2":
        _check_missing([
            ("m", m), ("kappa", kappa), ("a", a),
            ("z", z), ("F", F), ("zeta", zeta), ("R", R), ("T", T)
        ])
        m, kappa, a, z, F, zeta, R, T = validate_inputs(m, kappa, a, z, F, zeta, R, T)
        arg = safe_divide(z * F * zeta, 2 * R * T)
        cosh_term = np.cosh(arg) - 1
        factor = 2 * safe_divide(1 + 3 * m, z**2)
        return factor * kappa * a * cosh_term

    else:  # mode 3
        _check_missing([
            ("kappa", kappa), ("a", a), ("z", z), ("F", F), ("zeta", zeta),
            ("R", R), ("T", T), ("epsilon0", epsilon0), ("epsilonm", epsilonm),
            ("eta", eta), ("D", D)
        ])
        kappa, a, z, F, zeta, R, T, epsilon0, epsilonm, eta, D = validate_inputs(
            kappa, a, z, F, zeta, R, T, epsilon0, epsilonm, eta, D
        )
        numerator_m = 2 * epsilon0 * epsilonm * (R**2) * (T**2)
        denominator_m = 3 * eta * (F**2) * D
        m_calc = safe_divide(numerator_m, denominator_m)
        arg = safe_divide(z * F * zeta, 2 * R * T)
        cosh_term = np.cosh(arg) - 1
        factor = 2 * safe_divide(1 + 3 * m_calc , z**2)
        return factor * kappa * a * cosh_term

def eckert(u, cp, delta_T):
    """
    Calculates the Eckert number (Ec), which represents the ratio of advective transport 
    to heat dissipation potential in a flowing continuum.

    Ec = u^2 / (cp * delta_T)

    Parameters:
        u : float or array-like
            Local flow velocity (m/s)
        cp : float or array-like
            Specific heat at constant pressure (J/kg·K)
        delta_T : float or array-like
            Temperature difference between wall and local temperature (K)

    Returns:
        Ec : float or ndarray
            Eckert number, with np.nan propagated.

    Raises:
        ValueError: if any input is None or missing.
    """
    # Validate inputs
    if any(x is None for x in (u, cp, delta_T)):
        raise ValueError("All inputs 'u', 'cp', and 'delta_T' must be provided and not None.")

    u, cp, delta_T = validate_inputs(u, cp, delta_T)

    numerator = u ** 2
    denominator = cp * delta_T

    return safe_divide(numerator, denominator)

def ekman(*, mode="mode 1", D=None, nu=None,  L=None, Omega=None, phi=None, Ro=None, Re=None):
    """
    Calculates the Ekman number (Ek), a dimensionless number describing the ratio of viscous 
    to Coriolis forces in a rotating fluid system. Four modes are supported:

    Modes:
        mode 1:
            Ek = nu / (2 * D^2 * Omega * sin(phi))
            Parameters required: nu, D, Omega, phi (radians)
        mode 2 (Tritton):
            Ek = nu / (Omega * L^2)
            Parameters required: nu, L, Omega
        mode 3 (NRL Plasma Formulary):
            Ek = sqrt(nu / (2 * Omega * L^2))
            Parameters required: nu, L, Omega
        mode 4:
            Ek = sqrt(Ro / Re)
            Parameters required: Ro, Re

    Parameters:
        nu : float or array-like
            Kinematic viscosity (m^2/s)
        mode : str, optional (default='mode 1')
            Calculation mode: 'mode 1', 'mode 2', 'mode 3', or 'mode 4'
        D : float or array-like, required for mode 1
            Characteristic length scale (m)
        L : float or array-like, required for modes 2 and 3
            Characteristic length scale (m)
        Omega : float or array-like, required for modes 1, 2, 3
            Angular velocity (rad/s)
        phi : float or array-like, required for mode 1
            Latitude (radians)
        Ro : float or array-like, required for mode 4
            Rossby number
        Re : float or array-like, required for mode 4
            Reynolds number

    Returns:
        Ek : float or ndarray
            Ekman number, with np.nan propagated.

    Raises:
        ValueError: If required parameters are missing or mode is invalid.
    """
    if mode == "mode 1":
        if any(x is None for x in (nu, D, Omega, phi)):
            raise ValueError("Parameters 'nu', 'D', 'Omega', and 'phi' are required for mode 1.")
        nu, D, Omega, phi = validate_inputs(nu, D, Omega, phi)
        denom = 2 * (D ** 2) * Omega * np.sin(phi)
        return safe_divide(nu, denom)

    elif mode == "mode 2":
        if any(x is None for x in (nu, L, Omega)):
            raise ValueError("Parameters 'nu', 'L', and 'Omega' are required for mode 2.")
        nu, L, Omega = validate_inputs(nu, L, Omega)
        denom = Omega * (L ** 2)
        return safe_divide(nu, denom)

    elif mode == "mode 3":
        if any(x is None for x in (nu, L, Omega)):
            raise ValueError("Parameters 'nu', 'L', and 'Omega' are required for mode 3.")
        nu, L, Omega = validate_inputs(nu, L, Omega)
        inside_sqrt = safe_divide(nu, 2 * Omega * (L ** 2))
        # For nan propagation, if inside_sqrt is nan, np.sqrt will propagate that
        return np.sqrt(inside_sqrt)

    elif mode == "mode 4":
        if any(x is None for x in (Ro, Re)):
            raise ValueError("Parameters 'Ro' and 'Re' are required for mode 4.")
        Ro, Re = validate_inputs(Ro, Re)
        inside_sqrt = safe_divide(Ro, Re)
        return np.sqrt(inside_sqrt)

    else:
        raise ValueError("Invalid mode. Choose 'mode 1', 'mode 2', 'mode 3', or 'mode 4'.")

def ericksen(mu, v, L, K):
    """
    Calculates the Ericksen number (Er).

    Er = (μ * v * L) / K

    where:
        μ : float or array-like
            Dynamic viscosity of the fluid (Pa·s)
        v : float or array-like
            Characteristic velocity scale (m/s)
        L : float or array-like
            Characteristic length scale (m)
        K : float or array-like
            Elasticity force (e.g., elasticity modulus times an area)

    Returns:
        Er : float or ndarray
            Ericksen number, with np.nan propagated.

    Raises:
        ValueError: if any input is None
    """
    if any(x is None for x in (mu, v, L, K)):
        raise ValueError("All parameters mu, v, L, and K must be provided.")

    mu, v, L, K = validate_inputs(mu, v, L, K)
    return safe_divide(mu * v * L, K)

def euler(pu, pd, rho, v, *, mode="mode 1"):
    """
    Calculates the Euler number (Eu) in two common modes.

    Mode 1:
        Eu = (p_u - p_d) / (rho * v^2)

    Mode 2:
        Eu = (p_u - p_d) / (0.5 * rho * v^2)

    Parameters:
        pu : float or array-like
            Upstream pressure (Pa)
        pd : float or array-like
            Downstream pressure (Pa)
        rho : float or array-like
            Fluid density (kg/m^3)
        v : float or array-like
            Characteristic flow velocity (m/s)
        mode : str, optional (default: "mode 1")
            Calculation mode: "mode 1" or "mode 2"

    Returns:
        Eu : float or ndarray
            Euler number, with np.nan propagated.

    Raises:
        ValueError: if any required parameter is missing or mode is invalid
    """
    if any(x is None for x in (pu, pd, rho, v)):
        raise ValueError("All parameters pu, pd, rho, and v must be provided.")

    pu, pd, rho, v = validate_inputs(pu, pd, rho, v)

    delta_p = pu - pd

    if mode == "mode 1":
        denominator = rho * v**2
    elif mode == "mode 2":
        denominator = 0.5 * rho * v**2
    else:
        raise ValueError("Invalid mode. Choose 'mode 1' or 'mode 2'.")

    return safe_divide(delta_p, denominator)

def excess_temperature_coefficient(cp, T, Te, Ue):
    """
    Calculates the Excess Temperature Coefficient (Θr).

    Θr = (cp * (T - Te)) / (Ue^2 / 2)

    Parameters:
        cp : float or array-like
            Specific heat at constant pressure (J/kg·K)
        T : float or array-like
            Local temperature (K)
        Te : float or array-like
            Reference temperature (K)
        Ue : float or array-like
            Characteristic velocity scale (m/s)

    Returns:
        Θr : float or ndarray
            Excess Temperature Coefficient, with np.nan propagated.

    Raises:
        ValueError: if any required parameter is missing
    """
    if any(x is None for x in (cp, T, Te, Ue)):
        raise ValueError("All parameters cp, T, Te, and Ue must be provided.")

    cp, T, Te, Ue = validate_inputs(cp, T, Te, Ue)

    numerator = cp * (T - Te)
    denominator = (Ue**2) / 2

    return safe_divide(numerator, denominator)

def fanning_friction_factor(*, mode="mode 1", Re = None, epsilon=None, D=None, f_init=0.02, max_iter=100, tol=1e-6):
    """
    Calculate the Fanning friction factor using various correlations depending on flow regime and pipe characteristics.

    Parameters
    ----------
    mode : str
        The calculation mode specifying which formula to use:
        Mode 1: Laminar flow in round tubes
            f = 16 / Re
        Mode 2: Laminar flow in square channels
            f = 14.227 / Re
        Mode 3: Turbulent flow in hydraulically smooth pipes (Blasius)
            f = 0.0791 / Re^0.25, valid for 2100 < Re < 1e5
        Mode 4: Turbulent flow with Koo correlation
            f = 0.0014 + 0.125 / Re^0.32, valid for 1e4 < Re < 1e7
        Mode 5: Rough pipes using Haaland equation
            1/sqrt(f) = -3.6 * log10(6.9/Re + (epsilon/D / 3.7)^(10/9))
        Mode 6: Swamee–Jain explicit equation (approximation of Colebrook)
            f = 0.0625 / [log10(epsilon/D / 3.7 + 5.74 / Re^0.9)]^2
        Mode 7: Fully rough turbulent flow (Nikuradse)
            1/sqrt(f) = 2.28 - 4.0 * log10(epsilon/D)
        Mode 8: Implicit Colebrook equation (iterative solution)
            1/sqrt(f) = -4.0 * log10(epsilon/D / 3.7 + 1.255 / (Re * sqrt(f)))

    Re : float or np.ndarray
        Reynolds number (dimensionless).
    epsilon : float, optional
        Pipe roughness (length units), default is 0.
    D : float, optional
        Pipe diameter (length units), default is 1.
    f_init : float, optional
        Initial guess for friction factor in iterative mode (mode 8), default is 0.02.
    max_iter : int, optional
        Maximum number of iterations for mode 8, default is 100.
    tol : float, optional
        Tolerance for convergence in mode 8, default is 1e-6.

    Returns
    -------
    f : float or np.ndarray
        Calculated Fanning friction factor.
    """
    # Ensure Re is numpy array for vectorization
    Re = np.asarray(Re, dtype=np.float64)

    if mode == "mode 1":
        # Laminar flow, round tubes
        return safe_divide(16.0, Re)

    elif mode == "mode 2":
        # Laminar flow, square channel
        return safe_divide(14.227, Re)

    elif mode == "mode 3":
        # Turbulent, hydraulically smooth pipes (Blasius)
        return safe_divide(0.0791, Re**0.25)

    elif mode == "mode 4":
        # Turbulent flow, Koo correlation
        return 0.0014 + safe_divide(0.125, Re**0.32)

    elif mode == "mode 5":
        # Haaland equation for rough pipes
        if np.any(Re == 0):
            raise ValueError("Reynolds number must be nonzero for Haaland equation.")
        term1 = safe_divide(6.9, Re)
        term2 = safe_divide(safe_divide(epsilon, D), 3.7)
        frac = term1 + term2**(10.0/9.0)
        inv_sqrt_f = -3.6 * np.log10(frac)
        return safe_divide(1.0, inv_sqrt_f**2)

    elif mode == "mode 6":
        # Swamee–Jain explicit approximation
        term = safe_divide(safe_divide(epsilon, D), 3.7) + safe_divide(5.74, Re**0.9)
        f = safe_divide(0.0625, (np.log10(term)**2))
        return f

    elif mode == "mode 7":
        # Fully rough turbulent flow (Nikuradse)
        if epsilon == 0:
            raise ValueError("Pipe roughness epsilon must be > 0 for mode 7.")
        inv_sqrt_f = 2.28 - 4.0 * np.log10(safe_divide(epsilon, D))
        return safe_divide(1.0, inv_sqrt_f**2)

    elif mode == "mode 8":
        # Implicit Colebrook equation - iterative solution
        if np.any(Re == 0):
            f = np.nan
            print("Reynolds number must be nonzero for Colebrook equation.")
        f = np.full_like(Re, f_init, dtype=np.float64)

        for i in range(max_iter):
            inv_sqrt_f = safe_divide(1.0, np.sqrt(f))
            rhs = -4.0 * np.log10(safe_divide(safe_divide(epsilon, D), 3.7) + safe_divide(1.255, (Re * np.sqrt(f))))
            f_new = safe_divide(1.0, rhs**2)

            # Check convergence
            if np.all(np.abs(f_new - f) < tol):
                break
            f = f_new

        else:
            print("Warning: Colebrook iteration did not converge within max_iter")

        return f

    else:
        raise ValueError(f"Unsupported mode: {mode}. Choose modes 1 through 8.")

def froude(*,
           mode="classical",
           u=None, g=9.80665, L=None, V=None,
           U=None, A=None, B=None, d=None,
           beta=None, h=None, s_g=None, x_d=None, x=None,
           omega=None, r=None,
           g_prime=None,
           v=None, l=None, f=None):
    """
    Calculates the Froude number in various modes depending on the flow/application context.

    The Froude number (Fr) is a dimensionless number expressing the ratio of flow inertia to external force fields,
    often gravity.

    Modes and formulas:

    - classical:
        Fr = u / sqrt(g * L)
        Parameters required: u, L, optional g (default 9.80665)

    - displacement:
        Fr = u / sqrt(g * V^(1/3))
        Parameters required: u, V, optional g

    - shallow_water:
        Fr = U / sqrt(g * (A / B))
        Parameters required: U, A, B, optional g

    - shallow_water_simplified:
        Fr = U / sqrt(g * d)
        Parameters required: U, d, optional g

    - extended:
        Fr = u / sqrt(beta * h + s_g * (x_d - x))
        Parameters required: u, beta, h, s_g, x_d, x

    - stirred_tank:
        Fr = omega * sqrt(r / g)
        Parameters required: omega, r, optional g

    - densimetric:
        Fr = u / sqrt(g_prime * h)
        Parameters required: u, g_prime, h

    - walking_velocity:
        Fr = v**2 / (g * l)
        Parameters required: v, l, optional g

    - walking_frequency:
        Fr = l * f**2 / g
        Parameters required: l, f, optional g

    Parameters
    ----------
    mode : str
        Calculation mode, one of ['classical', 'displacement', 'shallow_water', 'shallow_water_simplified',
                                   'extended', 'stirred_tank', 'densimetric', 'walking_velocity', 'walking_frequency']

    u : float or array-like, optional
        Flow velocity (m/s) for modes classical, displacement, extended, densimetric

    g : float or array-like, optional, default=9.80665
        Gravity acceleration (m/s^2)

    L : float or array-like, optional
        Characteristic length (m) for classical mode

    V : float or array-like, optional
        Volume (m^3) for displacement mode

    U : float or array-like, optional
        Average flow velocity (m/s) for shallow_water modes

    A : float or array-like, optional
        Cross-sectional area (m^2) for shallow_water mode

    B : float or array-like, optional
        Free-surface width (m) for shallow_water mode

    d : float or array-like, optional
        Depth (m) for shallow_water_simplified mode

    beta : float or array-like, optional
        Parameter β = g K cos ζ for extended mode

    h : float or array-like, optional
        Height (m) for extended and densimetric modes

    s_g : float or array-like, optional
        Parameter s_g = g sin ζ for extended mode

    x_d : float or array-like, optional
        Downslope distance where flow hits horizontal datum (m) for extended mode

    x : float or array-like, optional
        Channel downslope position (m) for extended mode

    omega : float or array-like, optional
        Impeller frequency (rad/s or rpm) for stirred_tank mode

    r : float or array-like, optional
        Impeller radius (m) for stirred_tank mode

    g_prime : float or array-like, optional
        Effective gravity for densimetric mode

    v : float or array-like, optional
        Velocity (m/s) for walking_velocity mode

    l : float or array-like, optional
        Characteristic length (m) for walking modes

    f : float or array-like, optional
        Stride frequency (Hz) for walking_frequency mode

    Returns
    -------
    Fr : float or ndarray
        Calculated Froude number(s), with np.nan propagation.

    Raises
    ------
    ValueError
        If required parameters for the selected mode are missing or mode is invalid.
    """
    # Validate mode input
    valid_modes = {
        "classical", "displacement", "shallow_water", "shallow_water_simplified",
        "extended", "stirred_tank", "densimetric", "walking_velocity", "walking_frequency"
    }
    if mode not in valid_modes:
        raise ValueError(f"Invalid mode '{mode}'. Choose from {valid_modes}.")

    # Validate inputs helper shortcut for single or multiple inputs
    def val(*args):
        return validate_inputs(*args)

    # For NaN propagation helper: if any input has np.nan return np.nan early
    def any_nan(*args):
        for arg in args:
            if arg is not None:
                arr = np.asarray(arg)
                if np.isnan(arr).any():
                    return True
        return False

    # Classical mode: Fr = u / sqrt(g * L)
    if mode == "classical":
        if u is None or L is None:
            raise ValueError("Parameters 'u' and 'L' must be provided for mode='classical'")
        u, L, g = val(u, L, g)
        if any_nan(u, L, g):
            return np.nan
        return safe_divide(u, np.sqrt(g * L))

    # Displacement mode: Fr = u / sqrt(g * V^(1/3))
    elif mode == "displacement":
        if u is None or V is None:
            raise ValueError("Parameters 'u' and 'V' must be provided for mode='displacement'")
        u, V, g = val(u, V, g)
        if any_nan(u, V, g):
            return np.nan
        length = np.cbrt(V)
        return safe_divide(u, np.sqrt(g * length))

    # Shallow water: Fr = U / sqrt(g * (A/B))
    elif mode == "shallow_water":
        if U is None or A is None or B is None:
            raise ValueError("Parameters 'U', 'A' and 'B' must be provided for mode='shallow_water'")
        U, A, B, g = val(U, A, B, g)
        if any_nan(U, A, B, g):
            return np.nan
        denom = g * safe_divide(A, B)
        return safe_divide(U, np.sqrt(denom))

    # Shallow water simplified: Fr = U / sqrt(g * d)
    elif mode == "shallow_water_simplified":
        if U is None or d is None:
            raise ValueError("Parameters 'U' and 'd' must be provided for mode='shallow_water_simplified'")
        U, d, g = val(U, d, g)
        if any_nan(U, d, g):
            return np.nan
        return safe_divide(U, np.sqrt(g * d))

    # Extended: Fr = u / sqrt(beta * h + s_g * (x_d - x))
    elif mode == "extended":
        if None in (u, beta, h, s_g, x_d, x):
            raise ValueError("Parameters 'u', 'beta', 'h', 's_g', 'x_d', and 'x' must be provided for mode='extended'")
        u, beta, h, s_g, x_d, x = val(u, beta, h, s_g, x_d, x)
        if any_nan(u, beta, h, s_g, x_d, x):
            return np.nan
        denom = beta * h + s_g * (x_d - x)
        return safe_divide(u, np.sqrt(denom))

    # Stirred tank: Fr = omega * sqrt(r / g)
    elif mode == "stirred_tank":
        if omega is None or r is None:
            raise ValueError("Parameters 'omega' and 'r' must be provided for mode='stirred_tank'")
        omega, r, g = val(omega, r, g)
        if any_nan(omega, r, g):
            return np.nan
        return omega * np.sqrt(safe_divide(r, g))

    # Densimetric: Fr = u / sqrt(g_prime * h)
    elif mode == "densimetric":
        if u is None or g_prime is None or h is None:
            raise ValueError("Parameters 'u', 'g_prime', and 'h' must be provided for mode='densimetric'")
        u, g_prime, h = val(u, g_prime, h)
        if any_nan(u, g_prime, h):
            return np.nan
        return safe_divide(u, np.sqrt(g_prime * h))

    # Walking velocity: Fr = v^2 / (g * l)
    elif mode == "walking_velocity":
        if v is None or l is None:
            raise ValueError("Parameters 'v' and 'l' must be provided for mode='walking_velocity'")
        v, l, g = val(v, l, g)
        if any_nan(v, l, g):
            return np.nan
        numerator = v**2
        denominator = g * l
        return safe_divide(numerator, denominator)

    # Walking frequency: Fr = l * f^2 / g
    elif mode == "walking_frequency":
        if l is None or f is None:
            raise ValueError("Parameters 'l' and 'f' must be provided for mode='walking_frequency'")
        l, f, g = val(l, f, g)
        if any_nan(l, f, g):
            return np.nan
        numerator = l * (f**2)
        return safe_divide(numerator, g)

    import numpy.testing as npt

    def test_mode_classical():
        # Scalars
        u, L = 3.0, 2.0
        expected = 3.0 / np.sqrt(9.80665 * 2.0)
        out = froude(mode="classical", u=u, L=L)
        npt.assert_almost_equal(out, expected)

        # Arrays
        u = np.array([3.0, 4.0])
        L = 2.0
        expected = u / np.sqrt(9.80665 * L)
        out = froude(mode="classical", u=u, L=L)
        npt.assert_allclose(out, expected)

        # NaN propagation
        u = np.array([3.0, np.nan])
        out = froude(mode="classical", u=u, L=L)
        assert np.isnan(out[1])

        # Scalar+array
        u = 3.0
        L = np.array([2.0, 3.0])
        expected = u / np.sqrt(9.80665 * L)
        out = froude(mode="classical", u=u, L=L)
        npt.assert_allclose(out, expected)

    def test_invalid_mode():
        try:
            froude(mode="invalid", u=1, L=1)
        except ValueError as e:
            assert "Invalid mode" in str(e)
        else:
            assert False, "Expected ValueError for invalid mode"

    def test_displacement():
        u, V = 3.0, 27.0  # cube root = 3
        expected = 3.0 / np.sqrt(9.80665 * 3.0)
        out = froude(mode="displacement", u=u, V=V)
        npt.assert_almost_equal(out, expected)

    def test_stirred_tank():
        omega, r = 10.0, 0.5
        expected = omega * np.sqrt(r / 9.80665)
        out = froude(mode="stirred_tank", omega=omega, r=r)
        npt.assert_almost_equal(out, expected)

    def test_walking_velocity():
        v, l = 2.0, 1.0
        expected = (v**2) / (9.80665 * l)
        out = froude(mode="walking_velocity", v=v, l=l)
        npt.assert_almost_equal(out, expected)

    def test_walking_frequency():
        l, f = 1.0, 2.0
        expected = l * (f**2) / 9.80665
        out = froude(mode="walking_frequency", l=l, f=f)
        npt.assert_almost_equal(out, expected)

    def test_extended():
        u, beta, h, s_g, x_d, x = 2.0, 9.8, 1.0, 0.5, 10.0, 5.0
        denom = beta * h + s_g * (x_d - x)
        expected = u / np.sqrt(denom)
        out = froude(mode="extended", u=u, beta=beta, h=h, s_g=s_g, x_d=x_d, x=x)
        npt.assert_almost_equal(out, expected)

    def test_densimetric():
        u, g_prime, h = 2.0, 9.8, 1.0
        expected = u / np.sqrt(g_prime * h)
        out = froude(mode="densimetric", u=u, g_prime=g_prime, h=h)
        npt.assert_almost_equal(out, expected)

    # Run all tests
    test_mode_classical()
    test_invalid_mode()
    test_displacement()
    test_stirred_tank()
    test_walking_velocity()
    test_walking_frequency()
    test_extended()
    test_densimetric()

    print("All tests passed.")

def grashof(g, L, nu, *, mode="heat",
                   beta=None, Ts=None, T_inf=None,
                   beta_star=None, Ca_s=None, Ca_a=None):
    """
    Calculate Grashof number for heat transfer or mass transfer.

    Heat: Gr = g * beta * (Ts - T_inf) L^3 / nu^2
    Mass: Gr = g * beta_star * (Ca_s - Ca_a) L^3 / nu^2

    Parameters:
    -----------
    g : float or array-like
        Gravitational acceleration (m/s^2).
    L : float or array-like
        Characteristic length (m).
    nu : float or array-like
        Kinematic viscosity (m^2/s).
    mode : str
        'heat' for heat transfer Grashof number,
        'mass' for mass transfer Grashof number.
    beta : float or array-like, required if mode='heat'
        Volumetric thermal expansion coefficient (1/K).
    Ts : float or array-like, required if mode='heat'
        Surface temperature (K or °C).
    T_inf : float or array-like, required if mode='heat'
        Ambient/bulk temperature (K or °C).
    beta_star : float or array-like, required if mode='mass'
        Concentration expansion coefficient (1/concentration units).
    Ca_s : float or array-like, required if mode='mass'
        Surface concentration of species a.
    Ca_a : float or array-like, required if mode='mass'
        Ambient concentration of species a.

    Returns:
    --------
    Gr : float or np.ndarray
        Calculated Grashof number. NaNs propagated if inputs contain NaN.

    Raises:
    -------
    ValueError:
        If required parameters for the selected mode are not provided.
    """
    # Convert inputs to numpy arrays
    g, L, nu = validate_inputs(g, L, nu)

    # Check for mode and required parameters
    if mode == 'heat':
        if beta is None or Ts is None or T_inf is None:
            raise ValueError("For 'heat' mode, beta, Ts, and T_inf must be provided.")
        beta, Ts, T_inf = validate_inputs(beta, Ts, T_inf)
        delta_T = np.abs(Ts - T_inf)
        numerator = g * beta * delta_T * L**3
    elif mode == 'mass':
        if beta_star is None or Ca_s is None or Ca_a is None:
            raise ValueError("For 'mass' mode, beta_star, Ca_s, and Ca_a must be provided.")
        beta_star, Ca_s, Ca_a = validate_inputs(beta_star, Ca_s, Ca_a)
        delta_Ca = np.abs(Ca_s - Ca_a)
        numerator = g * beta_star * delta_Ca * L**3
    else:
        raise ValueError("Mode must be either 'heat' or 'mass'.")

    denominator = nu**2

    # Calculate Grashof number with safe division and NaN propagation
    with np.errstate(divide='ignore', invalid='ignore'):
        Gr = safe_divide(numerator, denominator)

    # Propagate NaN if any input in the calculation is NaN
    nan_mask = np.isnan(numerator) | np.isnan(denominator)
    if np.isscalar(Gr):
        if nan_mask:
            return np.nan
    else:
        Gr[nan_mask] = np.nan

    return Gr

def nusselt(h, L, k, *, mode="average", x=None):
    """
    Calculate the Nusselt number in two modes:
      - "average": Nu = h * L / k
      - "local": Nu_x = h_x * x / k

    Parameters:
    -----------
    h : float or array-like
        Convective heat transfer coefficient(s).
        For 'average', scalar or array-like broadcastable with L, k.
        For 'local', array-like.
    L : float or array-like
        Characteristic length(s).
    k : float or array-like
        Thermal conductivity(ies) of the fluid.
    mode : str, optional
        Mode of calculation, either "average" or "local".
        Default is "average".
    x : array-like, optional
        Positions along the length for local h_x values.
        Required for "local" mode.

    Returns:
    --------
    Nu : float or np.ndarray
        Calculated Nusselt number(s), with np.nan propagated.

    Raises:
    -------
    ValueError:
        If mode is invalid or if required inputs (like x) are missing for local mode.
    """
    import numpy as np

    if mode not in {"average", "local"}:
        raise ValueError(f"Invalid mode: {mode}. Choose from 'average' or 'local'.")

    #h = np.asarray(h, dtype=float)
    #k = np.asarray(k, dtype=float)
    h, k = validate_inputs(h, k)

    if mode == "average":
        L = validate_inputs(L)
        # Broadcast inputs
        h, L, k = np.broadcast_arrays(h, L, k)
        # Calculate Nu, np.nan propagate naturally in multiplication/division
        Nu = h * L / k
        return Nu

    # mode == "local"
    if x is None:
        raise ValueError("x positions must be provided for 'local' mode.")

    x = validate_inputs(x)
    # Broadcast all arrays to common shape
    try:
        h, x, k = np.broadcast_arrays(h, x, k)
    except ValueError as e:
        raise ValueError("h, x, and k inputs must be broadcast-compatible.") from e

    Nu = safe_divide(h * x, k)
    return Nu

def nusselt_integral(h, L, k):
    """
    Calculate average Nusselt number by numerically integrating convective heat
    transfer coefficient h over length L.

    Nu_avg = ( (1/L) * ∫ h_x dx ) * L / k

    Parameters:
    -----------
    L : float
        Characteristic length (scalar).
    h : array-like
        Convective heat transfer coefficients along length (vector).
        NaNs replaced by average of neighbors.
    k : float
        Thermal conductivity (scalar).

    Returns:
    --------
    Nu_avg : float
        Average Nusselt number, with np.nan propagated.
    """
    # Convert inputs
    L = float(L)
    k = float(k)
    h = np.asarray(h, dtype=float)

    # Propagate NaN if L or k is nan
    if np.isnan(L) or np.isnan(k):
        return np.nan

    # Replace NaNs in h by averaging neighbors
    h_corrected = h.copy()
    n = len(h_corrected)
    
    for i in range(n):
        if np.isnan(h_corrected[i]):
            # Find neighbors to average
            neighbors = []
            if i > 0 and not np.isnan(h_corrected[i - 1]):
                neighbors.append(h_corrected[i - 1])
            if i < n - 1 and not np.isnan(h_corrected[i + 1]):
                neighbors.append(h_corrected[i + 1])
            
            if neighbors:
                h_corrected[i] = np.mean(neighbors)
            else:
                # If no neighbors (all nan), fill with zero or keep nan? 
                # Here we keep nan to propagate downstream
                pass
    
    # If any NaNs remain (e.g., consecutive NaNs), propagate NaN output
    if np.any(np.isnan(h_corrected)):
        return np.nan

    # Define equally spaced positions along L for h values
    x = np.linspace(0, L, n)

    # Numerical integration using trapezoidal rule
    h_avg = np.trapz(h_corrected, x) / L

    # Calculate average Nusselt number
    Nu_avg = safe_divide(h_avg * L, k)

    return Nu_avg

def prandtl(cp, mu, k):
    """
    Calculate Prandtl number.

    Pr = (cp * mu) / k

    Parameters:
    -----------
    cp : float or array-like
        Specific heat capacity at constant pressure (J/(kg·K)).
    mu : float or array-like
        Dynamic viscosity (Pa·s or N·s/m²).
    k : float or array-like
        Thermal conductivity (W/(m·K)).

    Returns:
    --------
    Pr : float or np.ndarray
        Prandtl number, with NaN propagated if inputs contain NaN.

    Notes:
    ------

    """
    cp, mu, k = validate_inputs(cp, mu, k)

    numerator = cp * mu
    Pr = safe_divide(numerator, k)

    return Pr

def reynolds(u, L, *, mode="dynamic", nu=None, rho=None, mu=None):
    """
    Calculates the Reynolds number in either 'dynamic' or 'kinematic' mode.

    Re = rho * u * L / mu = u * L / nu

    Parameters:
        u : float or array-like
            Flow velocity (m/s)
        L : float or array-like
            Characteristic length (m)
        mode : str, optional (default: 'dynamic')
            Calculation mode: 'kinematic' or 'dynamic'
        nu : float or array-like, required for 'kinematic' mode
            Kinematic viscosity (m^2/s)
        rho : float or array-like, required for 'dynamic' mode
            Fluid density (kg/m^3)
        mu : float or array-like, required for 'dynamic' mode
            Dynamic viscosity (Pa·s)

    Returns:
        Re : float or ndarray
            Reynolds number, with np.nan propagated.

    Raises:
        ValueError: if required parameters are missing or mode is invalid
    """
    u, L = validate_inputs(u, L)

    if mode == "kinematic":
        if nu is None:
            raise ValueError("Kinematic viscosity 'nu' must be provided for mode='kinematic'")
        nu, = validate_inputs(nu)
        return safe_divide(u * L, nu)

    elif mode == "dynamic":
        if rho is None or mu is None:
            raise ValueError("Both 'rho' and 'mu' must be provided for mode='dynamic'")
        rho, mu = validate_inputs(rho, mu)
        return safe_divide(rho * u * L, mu)

    else:
        raise ValueError("Invalid mode. Choose 'kinematic' or 'dynamic'.")


    # Test data
    g = 9.81
    L = np.array([0.1, 0.2, 0.3])
    rho = np.array([1050, 1100, np.nan])
    rho_l = 1000

    nu = np.array([1e-6, 1.5e-6, 2e-6])
    mu = 1e-3

    # Test 1: Kinematic mode with vector/scalar mix
    ar_kin = archimedes(g, L, rho, rho_l, mode="kinematic", nu=nu)
    print("Kinematic Mode (vector/scalar mix):", ar_kin)

    # Test 2: Dynamic mode with vector/scalar mix
    ar_dyn = archimedes(g, L, rho, rho_l, mode="dynamic", mu=mu)
    print("Dynamic Mode (vector/scalar mix):", ar_dyn)

    # Test 3: NaN propagation (should show nan in third position)
    print("NaN Propagation Test (check third value):", ar_dyn)

    # Test 4: Scalar inputs
    ar_scalar = archimedes(9.81, 0.2, 1100, 1000, mode="kinematic", nu=1.5e-6)
    print("Kinematic Mode (all scalars):", ar_scalar)

    # Test 5: Error on missing nu in kinematic mode
    try:
        archimedes(g, L, rho, rho_l, mode="kinematic")
    except ValueError as e:
        print("Expected error (missing nu):", e)

    # Test 6: Error on missing mu in dynamic mode
    try:
        archimedes(g, L, rho, rho_l, mode="dynamic")
    except ValueError as e:
        print("Expected error (missing mu):", e)

    # Test 7: Invalid mode
    try:
        archimedes(g, L, rho, rho_l, mode="nonsense", mu=mu)
    except ValueError as e:
        print("Expected error (invalid mode):", e)

def rayleigh(
    *,
    mode="general",
    rho=None, beta=None, dT=None, l=None, g=None, eta=None, alpha=None,
    Ts=None, T_inf=None, x=None, nu=None,
    q_o=None, k=None,
    d_rho=None, rho0=None, K=None, L=None, R=None,
    H=None, D=None, Cp=None, dT_sa=None,
    Gr=None, Pr=None
):
    """
    Computes the Rayleigh number (Ra) in one of several physical contexts.

    Modes:
        - "general":
            Ra = (rho * beta * dT * l^3 * g) / (eta * alpha)

        - "vertical_wall":
            Ra = (g * beta * (Ts - T_inf) * x^3) / (nu * alpha)

        - "uniform_flux":
            Ra = (g * beta * q_o * x^4) / (nu * alpha * k)

        - "mushy_zone":
            Ra = (d_rho / rho0) * g * K * L / (alpha * nu)

        - "mushy_zone_alternate":
            Ra = (d_rho / rho0) * g * K / (R * nu)

        - "mantle_internal_heating":
            Ra = (g * rho0^2 * beta * H * D^5) / (eta * alpha * k)

        - "mantle_bottom_heating":
            Ra = (rho0^2 * g * beta * dT_sa * D^3 * Cp) / (eta * k)

        - "porous":
            Ra = (rho * beta * dT * k * l * g) / (eta * alpha)

        - "grpr":
            Ra = Gr * Pr

    Parameters:
        mode : str, optional (default "general")
            Mode to determine the formula used.
        All other parameters are optional and specific to the selected mode.

    Returns:
        Ra : float or ndarray
            Rayleigh number (dimensionless), with np.nan propagated.

    Raises:
        ValueError: if mode is invalid or required parameters are missing.
    """
    mode = mode.lower()
    if mode not in (
        "general", "vertical_wall", "uniform_flux",
        "mushy_zone", "mushy_zone_alternate",
        "mantle_internal_heating", "mantle_bottom_heating",
        "porous", "grpr"
    ):
        raise ValueError("Invalid mode. Choose from: general, vertical_wall, uniform_flux, "
                         "mushy_zone, mushy_zone_alternate, mantle_internal_heating, "
                         "mantle_bottom_heating, porous, grpr.")

    if mode == "general":
        missing = [n for n, v in (("rho", rho), ("beta", beta), ("dT", dT),
                                  ("l", l), ("g", g), ("eta", eta), ("alpha", alpha)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'general': {', '.join(missing)}")
        rho, beta, dT, l, g, eta, alpha = validate_inputs(rho, beta, dT, l, g, eta, alpha)
        return safe_divide(rho * beta * dT * l**3 * g, eta * alpha)

    elif mode == "vertical_wall":
        missing = [n for n, v in (("g", g), ("beta", beta), ("Ts", Ts),
                                  ("T_inf", T_inf), ("x", x), ("nu", nu), ("alpha", alpha)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'vertical_wall': {', '.join(missing)}")
        g, beta, Ts, T_inf, x, nu, alpha = validate_inputs(g, beta, Ts, T_inf, x, nu, alpha)
        return safe_divide(g * beta * (Ts - T_inf) * x**3, nu * alpha)

    elif mode == "uniform_flux":
        missing = [n for n, v in (("g", g), ("beta", beta), ("q_o", q_o),
                                  ("x", x), ("nu", nu), ("alpha", alpha), ("k", k)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'uniform_flux': {', '.join(missing)}")
        g, beta, q_o, x, nu, alpha, k = validate_inputs(g, beta, q_o, x, nu, alpha, k)
        return safe_divide(g * beta * q_o * x**4, nu * alpha * k)

    elif mode == "mushy_zone":
        missing = [n for n, v in (("d_rho", d_rho), ("rho0", rho0), ("g", g),
                                  ("K", K), ("L", L), ("alpha", alpha), ("nu", nu)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'mushy_zone': {', '.join(missing)}")
        d_rho, rho0, g, K, L, alpha, nu = validate_inputs(d_rho, rho0, g, K, L, alpha, nu)
        return safe_divide(safe_divide(d_rho, rho0) * g * K * L, alpha * nu)

    elif mode == "mushy_zone_alternate":
        missing = [n for n, v in (("d_rho", d_rho), ("rho0", rho0), ("g", g),
                                  ("K", K), ("R", R), ("nu", nu)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'mushy_zone_alternate': {', '.join(missing)}")
        d_rho, rho0, g, K, R, nu = validate_inputs(d_rho, rho0, g, K, R, nu)
        return safe_divide(safe_divide(d_rho, rho0) * g * K, R * nu)

    elif mode == "mantle_internal_heating":
        missing = [n for n, v in (("g", g), ("rho0", rho0), ("beta", beta),
                                  ("H", H), ("D", D), ("eta", eta), ("alpha", alpha), ("k", k)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'mantle_internal_heating': {', '.join(missing)}")
        g, rho0, beta, H, D, eta, alpha, k = validate_inputs(g, rho0, beta, H, D, eta, alpha, k)
        return safe_divide(g * rho0**2 * beta * H * D**5, eta * alpha * k)

    elif mode == "mantle_bottom_heating":
        missing = [n for n, v in (("rho0", rho0), ("g", g), ("beta", beta), ("dT_sa", dT_sa),
                                  ("D", D), ("Cp", Cp), ("eta", eta), ("k", k)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'mantle_bottom_heating': {', '.join(missing)}")
        rho0, g, beta, dT_sa, D, Cp, eta, k = validate_inputs(rho0, g, beta, dT_sa, D, Cp, eta, k)
        return safe_divide(rho0**2 * g * beta * dT_sa * D**3 * Cp, eta * k)

    elif mode == "porous":
        missing = [n for n, v in (("rho", rho), ("beta", beta), ("dT", dT),
                                  ("k", k), ("l", l), ("g", g), ("eta", eta), ("alpha", alpha)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'porous': {', '.join(missing)}")
        rho, beta, dT, k, l, g, eta, alpha = validate_inputs(rho, beta, dT, k, l, g, eta, alpha)
        return safe_divide(rho * beta * dT * k * l * g, eta * alpha)

    elif mode == "grpr":
        missing = [n for n, v in (("Gr", Gr), ("Pr", Pr)) if v is None]
        if missing:
            raise ValueError(f"Missing required parameter(s) for mode 'grpr': {', '.join(missing)}")
        Gr, Pr = validate_inputs(Gr, Pr)
        return Gr * Pr

def weber(rho, u, L, sigma):
    """
    Calculate Weber number.

    We = (rho * v^2 * l) / sigma

    Parameters:
    -----------
    rho : float or array-like
        Density of the fluid (kg/m³).
    v : float or array-like
        Velocity of the fluid (m/s).
    L : float or array-like
        Characteristic length, typically droplet diameter (m).
    sigma : float or array-like
        Surface tension of the fluid (N/m).

    Returns:
    --------
    We : float or np.ndarray
        Weber number, with NaN propagated if inputs contain NaN.

    Notes:
    ------
    The Weber number is a dimensionless number representing the ratio of 
    inertial forces to surface tension forces.
    """
    rho, u, L, sigma = validate_inputs(rho, u, L, sigma)

    numerator = rho * u**2 * L
    We = safe_divide(numerator, sigma)

    return We


if __name__ == "__main__":
    import numpy as np

    def print_test_result(mode, kwargs):
        try:
            result = rayleigh(mode=mode, **kwargs)
            print(f"Mode '{mode}' with inputs {kwargs} => Rayleigh number:\n{result}\n")
        except Exception as e:
            print(f"Mode '{mode}' with inputs {kwargs} raised an error:\n{e}\n")

    # Scalar values
    scalar_vals = {
        "rho": 1000, "beta": 0.0002, "dT": 10, "l": 0.1, "g": 9.81,
        "eta": 0.001, "alpha": 1.4e-7, "Ts": 310, "T_inf": 300, "x": 0.5,
        "nu": 1.0e-6, "q_o": 500, "k": 0.6, "d_rho": 50, "rho0": 1000,
        "K": 1e-12, "L": 0.05, "R": 1e-5, "H": 5e-8, "D": 2.9e6,
        "Cp": 1250, "dT_sa": 300, "Gr": 1e5, "Pr": 7
    }

    # Vector values
    vector_vals = {k: np.array([v, v * 2, np.nan]) for k, v in scalar_vals.items()}

    # Modes to test
    modes = [
        "general", "vertical_wall", "uniform_flux",
        "mushy_zone", "mushy_zone_alternate",
        "mantle_internal_heating", "mantle_bottom_heating",
        "porous", "grpr"
    ]

    # Testing scalar inputs
    print("=== Testing scalar inputs ===\n")
    for mode in modes:
        # Build kwargs for required parameters dynamically
        required_params = {
            "general": ["rho", "beta", "dT", "l", "g", "eta", "alpha"],
            "vertical_wall": ["g", "beta", "Ts", "T_inf", "x", "nu", "alpha"],
            "uniform_flux": ["g", "beta", "q_o", "x", "nu", "alpha", "k"],
            "mushy_zone": ["d_rho", "rho0", "g", "K", "L", "alpha", "nu"],
            "mushy_zone_alternate": ["d_rho", "rho0", "g", "K", "R", "nu"],
            "mantle_internal_heating": ["g", "rho0", "beta", "H", "D", "eta", "alpha", "k"],
            "mantle_bottom_heating": ["rho0", "g", "beta", "dT_sa", "D", "Cp", "eta", "k"],
            "porous": ["rho", "beta", "dT", "k", "l", "g", "eta", "alpha"],
            "grpr": ["Gr", "Pr"]
        }
        kwargs = {param: scalar_vals[param] for param in required_params[mode]}
        print_test_result(mode, kwargs)

    # Testing vector inputs
    print("=== Testing vector inputs ===\n")
    for mode in modes:
        kwargs = {param: vector_vals[param] for param in required_params[mode]}
        print_test_result(mode, kwargs)

    # Testing mixed inputs with np.nan introduced manually
    print("=== Testing mixed scalar and vector inputs with np.nan ===\n")
    for mode in modes:
        kwargs = {}
        for param in required_params[mode]:
            # Alternate scalar and vector for parameters, insert np.nan for some scalar
            if param in ("rho", "beta", "Gr"):  # example params to be scalar with nan
                val = scalar_vals[param]
                if param == "rho":
                    val = np.nan
                kwargs[param] = val
            else:
                kwargs[param] = vector_vals[param]
        print_test_result(mode, kwargs)

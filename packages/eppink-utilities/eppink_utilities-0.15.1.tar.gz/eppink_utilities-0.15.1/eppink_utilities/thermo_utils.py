from .math_utils import safe_divide
from .general_utils import validate_inputs
from .math_utils import error_catastrophic_cancellation

def mass_leakrate(*, mode="Mode 1", M=None, V=None, R=8.31446261815324, T=None, P=None, dPdt=None, dTdt=None, dRhodt=None, dRhodP=None, dRhodT=None, m=None, Rspecific=None):
    """
    Calculate mass leak rate (kg/s) from pressure change in an isochoric system with five modes.

    Modes and formulas:
        Mode 1:  m_dot = M * V / (R * T) * dP/dt                                (based on molar mass, moles)
        Mode 2:  m_dot = V * M / (R * T) * dRho/dt                              (based on density change)
        Mode 3:  m_dot = m / P * dP/dt                                          (relative pressure change)
        Mode 4:  m_dot = V / (Rspecific * T) * dP/dt                            (using specific gas constant)
        Mode 5:  m_dot = V * ( dRho/dt - dRho/dP|T dP/dt - dRho/dT|P dT/dt )    (Real gas)

        Ensure that all the derivatives are evaluated at the corresponding timestep.

    Parameters:
        mode : str, optional
            "Mode 1", "Mode 2", "Mode 3", "Mode4" or "Mode 5"
        M : float
            Molar mass (kg/mol)
        V : float
            Volume (m^3)
        R : float
            Universal gas constant (J/(mol·K))
        T : float
            Temperature (K)
        P : float
            Pressure (Pa)
        dPdt : array
            Pressure time derivative (Pa/s)
        dTdt : array
            Temperature time derivative (K/s)
        dRhodt : array
            Density time derivative (kg/m^3/s)
        dRhodP : array
            Density pressure derivative at constant temperature (kg/m^3Pa)
        dRhodT : array
            Density Temperature derivative at constant pressure (kg/m^3K)
        m : float
            Current mass (kg)
        Rspecific : float
            Specific gas constant (J/(kg·K))
        

    Returns:
        m_dot : float or ndarray
            Mass leak rate in kg/s.

    Raises:
        ValueError: if required parameters are missing or mode is invalid.
    """
    if mode == "Mode 1":
        if M is None or V is None or R is None or T is None or dPdt is None:
            raise ValueError("Mode 1 requires M, V, R, T, and dPdt")
        dPdt = validate_inputs(dPdt)
        M, V, R, T = validate_inputs(M, V, R, T, allow_array=False)
        dPdt, M, V, R, T = validate_inputs(dPdt, M, V, R, T, check_broadcast=True)
        return M * V / (R * T) * dPdt

    elif mode == "Mode 2":
        if V is None or M is None or R is None or T is None or dRhodt is None:
            raise ValueError("Mode 2 requires V, M, R, T, and dRhodt")
        dRhodt = validate_inputs(dRhodt)
        V, M, R, T = validate_inputs(V, M, R, T, allow_array=False)
        dRhodt, V, M, R, T = validate_inputs(dRhodt, V, M, R, T, check_broadcast=True)
        return V * M / (R * T) * dRhodt

    elif mode == "Mode 3":
        if m is None or P is None or dPdt is None:
            raise ValueError("Mode 3 requires m, P, and dPdt")
        dPdt = validate_inputs(dPdt)
        m, P = validate_inputs(m, P, allow_array=False)
        dPdt, m, P = validate_inputs(dPdt, m, P, check_broadcast=True)
        return safe_divide(m, P) * dPdt

    elif mode == "Mode 4":
        if V is None or Rspecific is None or T is None or dPdt is None:
            raise ValueError("Mode 4 requires V, Rspecific, T, and dPdt")
        dPdt = validate_inputs(dPdt)
        V, Rspecific, T = validate_inputs(V, Rspecific, T, allow_array=False)
        dPdt, V, Rspecific, T = validate_inputs(dPdt, V, Rspecific, T, check_broadcast=True)
        return V / (Rspecific * T) * dPdt
    
    elif mode == "Mode 5":
        if V is None or dRhodt is None or dRhodP is None or dRhodT is None or dPdt is None or dTdt is None:
            raise ValueError("Mode 4 requires V, dRhodt, dRhodP, dRhodT, dPdt and dTdt")
        dRhodt, dRhodP, dRhodT, dPdt, dTdt = validate_inputs(dRhodt, dRhodP, dRhodT, dPdt, dTdt)
        V = validate_inputs(V, allow_array=False)
        V, dRhodt, dRhodP, dRhodT, dPdt, dTdt = validate_inputs(V, dRhodt, dRhodP, dRhodT, dPdt, dTdt, check_broadcast=True)
        return V * (dRhodt - dRhodP * dPdt - dRhodT * dTdt)

    else:
        raise ValueError("Invalid mode. Choose 'Mode 1', 'Mode 2', 'Mode 3', 'mode4', or 'Mode 5'.")


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    import eppink_utilities as EU
    import CoolProp.CoolProp as CP

    # Time vector
    dt = 0.1  # seconds
    n_points = 1000
    t = np.linspace(0, dt * (n_points - 1), n_points)  # total duration: 9.9 s

    # Pressure data (Pa) - oscillations around atmospheric pressure
    P = 101325 - 50000 * np.sin(0.025 * t)


    # Temperature data (K) - slow ramp + oscillations
    T = 300 + 0 * t

    # Compute derivatives of density w.r.t. T and P, and density itself
    # NOTE: PropsSI may not support vectorized inputs, so we do elementwise
    dRhodT = np.array([CP.PropsSI('d(D)/d(T)|P', 'P', p, 'T', temp, 'N2') for p, temp in zip(P, T)])
    dRhodP = np.array([CP.PropsSI('d(D)/d(P)|T', 'P', p, 'T', temp, 'N2') for p, temp in zip(P, T)])
    Rho = np.array([CP.PropsSI('D', 'P', p, 'T', temp, 'N2') for p, temp in zip(P, T)])

    # Compute time derivatives using your finite difference method
    A = EU.math_utils.derivative_FDM(Rho, t, 1, 6)
    dRhodt = A["derivative"]
    errorest = A["error_estimation"]
    B = EU.math_utils.derivative_FDM(P, t, 1, 6)
    dPdt = B["derivative"]
    C = EU.math_utils.derivative_FDM(T, t, 1, 6)
    dTdt = C["derivative"]



    # Calculate mass leak rate (Mode 5)
    dmdt = EU.thermo_utils.mass_leakrate(
        mode="Mode 5",
        dPdt=dPdt,
        dTdt=dTdt,
        dRhodt=dRhodt,
        dRhodT=dRhodT,
        dRhodP=dRhodP,
        V=1.0  # Add volume or any other required parameters if needed
    )

    Cerror = EU.math_utils.error_catastrophic_cancellation(dRhodt,(dRhodT * dTdt + dRhodP * dPdt),errorest,errorest)

    plt.figure(figsize=(18, 8))

    # Row 1
    plt.subplot(2, 3, 1)
    plt.plot(t, P)
    plt.title("Pressure vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Pressure (Pa)")

    plt.subplot(2, 3, 2)
    plt.plot(t, dRhodP)
    plt.title("dRhodP vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("dRhodP (not K)")

    plt.subplot(2, 3, 3)
    plt.plot(t, dmdt)
    plt.title("Mass Leak Rate vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Mass Leak Rate (kg/s)")

    # Row 2
    plt.subplot(2, 3, 4)
    plt.plot(t, dPdt)
    plt.title("dP/dt vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("dP/dt (Pa/s)")

    plt.subplot(2, 3, 5)
    plt.plot(t, dRhodt)
    plt.title("dRho/dt vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("dRho/dt (kg/m^3/s)")

    plt.subplot(2, 3, 6)
    plt.plot(t, errorest)
    plt.title("catastrophic cancellation error vs Time")
    plt.xlabel("Time (s)")
    plt.ylabel("CCE")




    plt.tight_layout()
    plt.show()



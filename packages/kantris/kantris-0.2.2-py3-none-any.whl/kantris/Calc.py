import numpy as np
from scipy.integrate import odeint
from typing import Sequence, Callable, Optional, Any

class Calc:
    VERSION = 'Kantris.Calc: 0.1.3'
    class ODE:
        """
        Numerically solves a System of Ordinary Differential Equations\n
        T() Sets a List of the values of T to be calculated \n
        Func() Sets the Function to be solved for. Must be in format func(y, t, *Args) \n
        Args() Sets the arguments for Func() \n
        Y0() Sets the starting paramters. Must match the Dimension of Func() \n
        Run() solves the ODE and returns a list of lists in format [t, y1, y2, ...] \n
        """
        def __init__(self):
            self.t: Optional[Sequence[float]] = None
            self.y0: Optional[Sequence[float]] = None
            self.args: tuple[Any, ...] = ()
            self.func: Optional[Callable[..., Sequence[float]]] = None
    
        def T(self, t: Sequence[float]):
            self.t = t
            return self
        def Y0(self, y0: Sequence[float]):
            self.y0 = y0
            return self
        def Args(self, args: tuple[Any, ...]):
            self.args = args
            return self
        def Func(self, func: Callable[..., Sequence[float]]):
            """
            Example for a 2-Dimensional ODE with 2 Args/Variables (harmonic oszilator with friction): \n
            def diffEq(y, t, A, B):
                d1, d2 = y
                dydt = [d2, -A*d1 - B*d2]
                return dydt
            """
            self.func = func
            return self


        def Run(self) -> np.ndarray:
            # Check required fields
            missing = [f for f in ("t", "y0", "func") if getattr(self, f) is None]
            if missing:
                raise RuntimeError(f"Missing parameters: {', '.join(missing)}")
            # Solve
            sol = odeint(self.func, self.y0, self.t, args=self.args)
            # Optional: return t alongside solution
            return np.column_stack((self.t, sol))
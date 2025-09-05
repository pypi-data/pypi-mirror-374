import numpy as np
from typing import Optional, Dict, Any, Tuple

from .optimization import golden_section_search
from .fracdiff import fracdiff
from .lw import LW


class TwoStepELW:
    """
    Two-step Exact Local Whittle estimator of Shimotsu (2010).

    References
    ----------
    Shimotsu, K. (2010). Exact Local Whittle Estimation of Fractional
    Integration with Unknown Mean and Time Trend. _Econometric Theory_ 26,
    501--540.

    Hurvich, C. M., and W. W. Chen (2000). An Efficient Taper for Potentially
    Overdifferenced Long-Memory Time Series. _Journal of Time Series Analysis_
    21, 155--180.

    Velasco, C. (1999). Gaussian Semiparametric Estimation for Non-Stationary
    Time Series. _Journal of Time Series Analysis_ 20, 87--126.
    """

    def weight_function(self, d: float) -> float:
        """
        Compute weight function w(d) for adaptive mean estimation.

        Parameters
        ----------
        d : float
            Memory parameter estimate

        Returns
        -------
        float
            Weight value for adaptive mean estimation

        Notes
        -----
        Following Shimotsu (2010), the weight function is:
        w(d) = 1 for d <= 0.5 (sample mean for stationary series)
        w(d) = 0 for d >= 0.75 (first observation for persistent series)
        w(d) = (1/2)[1 + cos(-2*pi+4*pi*d)] for d in (0.5, 0.75) (smooth transition)

        This matches the original Matlab implementation in ewhittle.m:
        weight = (d<=0.5) + (1/2)*(1 + cos(-2*pi+4*pi*d))*(d>0.5)*(d<0.75)
        """
        if d <= 0.5:
            return 1.0
        elif d < 0.75:
            return 0.5 * (1.0 + np.cos(-2*np.pi + 4*np.pi*d))
        else:
            return 0.0

    def detrend(self, X: np.ndarray, order: int = 0) -> np.ndarray:
        """
        Remove time trend of specified order.

        Following Shimotsu (2010) Section 4.2, we regress X_t on
        (1, t, t^2, ..., t^k) and return residuals.

        Parameters
        ----------
        X : np.ndarray
            Time series data
        order : int, optional
            Order of time trend to remove.  For order=0,
            we remove a constant (demean).

        Returns
        -------
        np.ndarray
            Detrended time series
        """
        if order == 0:
            return X - np.mean(X)  # Demean only

        n = len(X)

        # Create polynomial trend regressors: (1, t, t^2, ..., t^order)
        t = np.arange(1, n+1, dtype=np.float64)

        # Design matrix: each column is t^i for i = 0, 1, ..., order
        Z = np.ones((n, order + 1), dtype=np.float64)
        for i in range(1, order + 1):
            Z[:, i] = t ** i

        # OLS regression: X = Z*beta + residuals
        # beta = (Z'Z)^(-1) Z'X
        ZtZ = Z.T @ Z
        ZtX = Z.T @ X

        try:
            beta = np.linalg.solve(ZtZ, ZtX)
            X_fitted = Z @ beta
            X_detrended = X - X_fitted
        except np.linalg.LinAlgError:
            # Fallback to pseudoinverse if singular
            beta = np.linalg.pinv(Z) @ X
            X_fitted = Z @ beta
            X_detrended = X - X_fitted

        return X_detrended

    def objective(self, d: float, x: np.ndarray, m: int) -> float:
        """
        Exact local Whittle objective function.

        Parameters
        ----------
        d : float
            Memory parameter
        x : np.ndarray
            Time series data (already demeaned/detrended residuals)
        m : int
            Number of frequencies to use

        Returns
        -------
        float
            Objective function value to be minimized
        """
        # Mean correction for detrended residuals following Shimotsu (2010) Section 4.2:
        # Since detrended residuals sum to zero, use simplified correction
        # \phi(d) = (1 - w(d)) X_1
        weight = self.weight_function(d)
        myu = (1 - weight) * x[0]
        x_corrected = x - myu

        # ELW objective function
        dx = fracdiff(x_corrected, d)
        n = len(dx)
        t = np.arange(0, n, dtype=np.float64)  # t = (0:1:n-1)'
        lam = 2 * np.pi * t / n  # lambda = 2*pi*t/n
        # wdx = (2*pi*n)^(-1/2)*conj(fft(conj(dx))).*exp(i*lambda)
        fft_dx = np.fft.fft(np.conj(dx))
        wdx = np.conj(fft_dx) * np.exp(1j * lam) / np.sqrt(2 * np.pi * n)
        lam_trunc = lam[1:m+1]
        vx = wdx[1:m+1]
        Iv = vx * np.conj(vx)
        g = np.sum(Iv) / m
        r = np.log(g) - 2 * d * np.sum(np.log(lam_trunc)) / m
        return float(r.real)

    def estimate(self, X: np.ndarray,
                 m: Optional[int] = None,
                 bounds: Optional[Tuple[float, float]] = (-1.0, 2.2),
                 taper: Optional[str] = None,
                 trend_order: Optional[int] = 0,
                 verbose: Optional[bool] = False) -> Dict[str, Any]:
        """
        Two-step exact local Whittle estimation.

        Parameters
        ----------
        X : np.ndarray
            Time series data
        m : int, optional
            Number of frequencies to use. Default m = n^0.65.
        bounds: tuple[float, float], optional
            Lower and upper bounds for golden section search
        taper : str, optional
            Type of taper for Stage 1. See the options in the LW.estimate() method.
            If None, uses 'hc'.
        trend_order : int, optional
            Order of polynomial detrending
        verbose : bool, optional
            Print diagnostic information

        Returns
        -------
        Dict[str, Any]
            Two-step ELW estimation results
        """
        X = np.asarray(X, dtype=np.float64)
        n = len(X)
        if taper is None:
            taper = 'hc'

        # Step 0: Detrending
        if verbose and trend_order > 0:
            print(f"Detrending with polynomial order {trend_order}")
        elif verbose:
            print("Demeaning data (detrend order 0)")
        X_detrended = self.detrend(X, trend_order)

        # Number of frequencies
        if m is None:
            m = round(n**0.65)
        if verbose:
            print(f"Using {m} frequencies for both steps")

        # Stage 1: Tapered local Whittle estimator
        if verbose:
            print(f"Stage 1: {taper} tapered LW estimation")
        X_step1 = X_detrended  # Stage 1 uses detrended data
        lw = LW()
        result_step1 = lw.estimate(X_step1, m=m, taper=taper, bounds=bounds)
        d_step1 = result_step1['d_hat']
        se_step1 = result_step1['se']
        if verbose:
            print(f"  Stage 1 estimate: d = {d_step1:.4f}")

        # Stage 2: Modified ELW estimation
        if verbose:
            print("Stage 2: Exact local whittle estimation")
            print(f"    Starting from Stage 1: d = {d_step1:.6f}")

        def step2_objective_func(d: float) -> float:
            return self.objective(d, X_detrended, m)

        # Use narrower bounds around the initial estimate
        local_bounds = (max(bounds[0], d_step1 - 2.576*se_step1), min(bounds[1], d_step1 + 2.576*se_step1))
        result_step2 = golden_section_search(step2_objective_func, brack=local_bounds)
        d_step2 = result_step2.x
        if verbose:
            print(f"    Final estimate: d = {d_step2:.4f}")

        # Two-Step ELW standard error
        se = 1 / (2 * np.sqrt(m))

        return {
            'n': n,
            'm': m,
            'd_hat': d_step2,
            'se': se,
            'ase': se,
            'method': '2elw',
            'taper': taper,
            'd_step1': d_step1,
            'nfev_step1': result_step1['nfev'],
            'objective_step1': result_step1.get('objective', np.nan),
            'nfev': result_step2.nfev,
            'objective': result_step2.fun,
            'trend_order': trend_order,
        }

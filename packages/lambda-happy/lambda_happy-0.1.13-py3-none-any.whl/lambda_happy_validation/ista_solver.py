from datetime import datetime
from typing import Dict, Any, List

import torch
import torch.nn.functional as F
import pandas as pd

from lambda_happy import LambdaHappy


class IstaSolver:
    """ISTA solver for sparse linear regression with optional LambdaHappy regularization."""

    def __init__(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        lambda_m: int = 10_000,
        lambda_nb_run: int = 500,
        max_iter: int = 1000,
        max_s: int = 10_000,
        eps: float = 1e-30,
        verbose: bool = False,
        version: str = "AUTOMATIC",
    ):
        """Initialize ISTA solver.

        Args:
            X (torch.Tensor): Feature matrix of shape (n, p).
            y (torch.Tensor): Target vector of shape (n,).
            lambda_m (int, optional): Number of samples for `LambdaHappy` aggregation. Defaults to 10_000.
            lambda_nb_run (int, optional): Number of runs for `LambdaHappy` estimation. Defaults to 500.
            max_iter (int, optional): Maximum number of ISTA iterations. Defaults to 1000.
            max_s (int, optional): Maximum number of step-size refinements per iteration. Defaults to 10_000.
            eps (float, optional): Convergence tolerance. Defaults to 1e-30.
            verbose (bool, optional): Whether to print progress logs. Defaults to False.
            version (str, optional): Version parameter passed to LambdaHappy. Defaults to "AUTOMATIC".
        """
        self.device = X.device
        n, p = X.shape
        self.X = X
        self.q = p + 1
        self.X_nq = torch.cat([torch.ones(n, 1, device=self.device), X], dim=1)
        self.y = y.view(-1)
        # Dummy lambda_happy estimation for reproducibility
        self.lambda_happy = LambdaHappy(X).compute_agg(
            nb_run=lambda_nb_run, m=lambda_m, version=version
        )
        self.max_iter = max_iter
        self.max_s = max_s
        self.eps = eps
        self.verbose = verbose

    @staticmethod
    def compute_tk(s: int) -> float:
        return 0.5**s

    @staticmethod
    def compute_grad_psi(
        X_nq: torch.Tensor, alpha: torch.Tensor, y: torch.Tensor
    ) -> torch.Tensor:
        r = X_nq @ alpha - y
        norm_r = r.norm(p=2)
        if norm_r == 0:
            return torch.zeros_like(alpha)
        return (X_nq.T @ r) / norm_r

    def compute_b(self, alpha: torch.Tensor, t: float) -> torch.Tensor:
        grad = self.compute_grad_psi(self.X_nq, alpha, self.y)
        return alpha - t * grad

    @staticmethod
    def compute_alpha_star(b: torch.Tensor, lam: float, t: float) -> torch.Tensor:
        a = b.clone()
        a[1:] = F.softshrink(b[1:], lam * t)
        return a

    def compute_phi(self, alpha: torch.Tensor) -> float:
        r = self.y - self.X_nq @ alpha
        return r.norm(p=2).pow(2) + self.lambda_happy * alpha[1:].abs().sum()

    def solve(self, init_alpha: torch.Tensor = None) -> torch.Tensor:
        """Run ISTA algorithm to estimate sparse coefficients.

        Args:
            init_alpha (torch.Tensor, optional): Initial coefficient vector.
                If None, initialized randomly with intercept = 0.

        Returns:
            torch.Tensor: Estimated coefficient vector (shape: (p+1,)).
        """
        if init_alpha is None:
            init_alpha = torch.randn(self.q, device=self.device)
            init_alpha[0] = 0.0

        alpha_k = init_alpha
        phi_k = self.compute_phi(alpha_k)

        for k in range(self.max_iter):
            for s in range(self.max_s):
                t = self.compute_tk(s)
                b = self.compute_b(alpha_k, t)
                alpha_s = self.compute_alpha_star(b, self.lambda_happy, t)
                phi_s = self.compute_phi(alpha_s)
                if phi_s < phi_k:
                    alpha_next, phi_next = alpha_s, phi_s
                    break
            else:
                alpha_next, phi_next = alpha_k, phi_k

            rel_diff = (alpha_next - alpha_k).norm(p=2)
            if rel_diff <= self.eps * alpha_next.norm(p=2):
                return alpha_next

            alpha_k, phi_k = alpha_next, phi_next

        return alpha_k


class IstaTestRunner:
    """Utility to test ISTA solver with synthetic data and generate reports."""

    def __init__(
        self,
        device_type: str = "cuda",
        dtype: torch.dtype = torch.float32,
        version: str = "AUTOMATIC",
    ) -> None:
        """Initialize test runner.

        Args:
            device_type (str, optional): Device type ("cpu" or "cuda"). Defaults to "cuda".
            dtype (torch.dtype, optional): Data type for tensors. Defaults to torch.float32.
            version (str, optional): Version parameter to pass to ISTA solver / LambdaHappy. Defaults to "AUTOMATIC".
        """
        self.device_type = device_type
        self.dtype = dtype
        self.version = version
        self.dtype_map = {torch.float32: "f32", torch.float16: "f16"}

    def run_test(self, n: int, p: int, seed: int, eps: float = 1e-6) -> Dict[str, Any]:
        """Run a single ISTA test with synthetic data.

        Args:
            n (int): Number of samples.
            p (int): Number of features.
            seed (int): Random seed.
            eps (float, optional): Convergence tolerance. Defaults to 1e-6.

        Returns:
            Dict[str, Any]: Dictionary with test results:
                - n, p, seed, num_needles
                - true_nonzero_idx, est_nonzero_idx
                - true_vals, est_vals
                - support_match (bool)
                - mse (float)
        """
        torch.manual_seed(seed)
        device = torch.device(self.device_type)
        X = torch.randn(n, p, device=device, dtype=self.dtype)

        alpha_true = torch.zeros(p + 1, device=device, dtype=self.dtype)
        alpha_true[0] = 1
        k = max(1, int(0.01 * p))
        indices = torch.randperm(p)[:k] + 1
        values = torch.rand(k, device=device, dtype=self.dtype) * (10 - 0.1) + 0.1
        for idx, val in zip(indices, values):
            alpha_true[idx] = val

        y = (
            X @ alpha_true[1:]
            + alpha_true[0]
            + torch.randn(n, device=device, dtype=self.dtype)
        )

        solver = IstaSolver(
            X, y, max_iter=1000, max_s=1000, eps=eps, version=self.version
        )
        alpha_est = solver.solve()

        true_support = sorted(
            (alpha_true[1:] != 0).nonzero(as_tuple=False).flatten().tolist()
        )
        est_support = sorted(
            (alpha_est[1:] != 0).nonzero(as_tuple=False).flatten().tolist()
        )
        support_match = set(true_support) == set(est_support)

        mse = torch.mean((y - (X @ alpha_est[1:] + alpha_est[0])) ** 2).item()

        true_vals = [float(alpha_true[i + 1]) for i in true_support]
        est_vals = [float(alpha_est[i + 1]) for i in est_support]

        return {
            "n": n,
            "p": p,
            "seed": seed,
            "num_needles": k,
            "true_nonzero_idx": true_support,
            "est_nonzero_idx": est_support,
            "true_vals": true_vals,
            "est_vals": est_vals,
            "support_match": support_match or len(est_support) < len(true_support),
            "mse": mse,
        }

    def run_all(self, p_list: List[int], seeds: List[int]) -> None:
        """Run multiple ISTA tests and export results to an HTML report.

        Args:
            p_list (List[int]): List of feature dimensions.
            seeds (List[int]): List of random seeds.
        """
        results = []
        for p in p_list:
            n = int(p / 2)
            for seed in seeds:
                res = self.run_test(n, p, seed)
                results.append(res)
        html = pd.DataFrame(results).to_html(
            index=False, border=1, classes="mystyle", justify="center"
        )
        full = f"""<!DOCTYPE html>
        <html><head><meta charset="utf-8">
        <style>
        table.mystyle {{
            border-collapse: collapse;
            width: 100%;
            font-family: Arial, sans-serif;
            font-size: 12px;
        }}
        table.mystyle th, table.mystyle td {{
            border: 1px solid #ccc;
            padding: 4px 6px;
            text-align: center;
        }}
        table.mystyle tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        </style></head><body>
        {html}
        </body></html>
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename_html = f"compute_multi_ista_solver_{self.version}_{self.device_type}_{self.dtype_map.get(self.dtype)}_{timestamp}.html".lower()
        with open(filename_html, "w", encoding="utf-8") as f:
            f.write(full)

        print(f"> HTML file generated : {filename_html}")

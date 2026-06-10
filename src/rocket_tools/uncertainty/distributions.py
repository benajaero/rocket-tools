"""Probability distributions for uncertainty propagation."""

from abc import ABC, abstractmethod

import numpy as np


class Distribution(ABC):
    @abstractmethod
    def sample(self, n: int, seed: int | None = None) -> np.ndarray: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict) -> "Distribution":
        dtype = data["distribution"]
        if dtype == "uniform":
            return Uniform(data["low"], data["high"])
        elif dtype == "normal":
            return Normal(data["mean"], data["std"])
        elif dtype == "lognormal":
            return LogNormal(data["mean"], data["sigma"])
        elif dtype == "truncated_normal":
            return TruncatedNormal(data["mean"], data["std"], data["low"], data["high"])
        else:
            raise ValueError(f"Unknown distribution: {dtype}")


class Uniform(Distribution):
    def __init__(self, low: float, high: float):
        self.low = low
        self.high = high

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.uniform(self.low, self.high, n)

    def to_dict(self) -> dict:
        return {"distribution": "uniform", "low": self.low, "high": self.high}


class Normal(Distribution):
    def __init__(self, mean: float, std: float):
        self.mean = mean
        self.std = std

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.normal(self.mean, self.std, n)

    def to_dict(self) -> dict:
        return {"distribution": "normal", "mean": self.mean, "std": self.std}


class LogNormal(Distribution):
    def __init__(self, mean: float, sigma: float):
        self.mean = mean
        self.sigma = sigma

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        return rng.lognormal(self.mean, self.sigma, n)

    def to_dict(self) -> dict:
        return {"distribution": "lognormal", "mean": self.mean, "sigma": self.sigma}


class TruncatedNormal(Distribution):
    def __init__(self, mean: float, std: float, low: float, high: float):
        self.mean = mean
        self.std = std
        self.low = low
        self.high = high

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        rng = np.random.default_rng(seed)
        samples = rng.normal(self.mean, self.std, n * 10)
        samples = samples[(samples >= self.low) & (samples <= self.high)]
        if len(samples) < n:
            raise ValueError("TruncatedNormal: too few samples in bounds")
        return samples[:n]

    def to_dict(self) -> dict:
        return {
            "distribution": "truncated_normal",
            "mean": self.mean,
            "std": self.std,
            "low": self.low,
            "high": self.high,
        }

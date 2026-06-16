"""Probability distributions for uncertainty propagation."""

import math
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

from rocket_tools.utils.validation import ValidationError


def _validate_sample_count(n: int) -> None:
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValidationError("Sample count must be a positive integer", "samples", "positive int")


def _validate_finite(value: Any, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(f"{name} must be numeric", name, "number")
    numeric_value = float(value)
    if not math.isfinite(numeric_value):
        raise ValidationError(f"{name} must be finite", name, "finite number")
    return numeric_value


def _require(data: dict, key: str) -> Any:
    if key not in data:
        raise ValidationError(f"Distribution is missing required field: {key}", key, "required")
    return data[key]


class Distribution(ABC):
    @abstractmethod
    def sample(self, n: int, seed: int | None = None) -> np.ndarray: ...

    @abstractmethod
    def to_dict(self) -> dict: ...

    @staticmethod
    def from_dict(data: dict) -> "Distribution":
        if not isinstance(data, dict):
            raise ValidationError("Distribution must be a mapping", "distribution", "mapping")
        dtype = data.get("distribution")
        if not isinstance(dtype, str):
            raise ValidationError(
                "Distribution must include a string 'distribution' field",
                "distribution",
                "string",
            )
        if dtype == "uniform":
            return Uniform(_require(data, "low"), _require(data, "high"))
        elif dtype == "normal":
            return Normal(_require(data, "mean"), _require(data, "std"))
        elif dtype == "lognormal":
            return LogNormal(_require(data, "mean"), _require(data, "sigma"))
        elif dtype == "truncated_normal":
            return TruncatedNormal(
                _require(data, "mean"),
                _require(data, "std"),
                _require(data, "low"),
                _require(data, "high"),
            )
        else:
            raise ValueError(f"Unknown distribution: {dtype}")


class Uniform(Distribution):
    def __init__(self, low: float, high: float):
        self.low = _validate_finite(low, "low")
        self.high = _validate_finite(high, "high")
        if self.low >= self.high:
            raise ValidationError("Uniform low must be less than high", "low", "< high")

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        _validate_sample_count(n)
        rng = np.random.default_rng(seed)
        return rng.uniform(self.low, self.high, n)

    def to_dict(self) -> dict:
        return {"distribution": "uniform", "low": self.low, "high": self.high}


class Normal(Distribution):
    def __init__(self, mean: float, std: float):
        self.mean = _validate_finite(mean, "mean")
        self.std = _validate_finite(std, "std")
        if self.std <= 0:
            raise ValidationError("Normal std must be greater than 0", "std", "> 0")

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        _validate_sample_count(n)
        rng = np.random.default_rng(seed)
        return rng.normal(self.mean, self.std, n)

    def to_dict(self) -> dict:
        return {"distribution": "normal", "mean": self.mean, "std": self.std}


class LogNormal(Distribution):
    def __init__(self, mean: float, sigma: float):
        self.mean = _validate_finite(mean, "mean")
        self.sigma = _validate_finite(sigma, "sigma")
        if self.sigma <= 0:
            raise ValidationError("LogNormal sigma must be greater than 0", "sigma", "> 0")

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        _validate_sample_count(n)
        rng = np.random.default_rng(seed)
        return rng.lognormal(self.mean, self.sigma, n)

    def to_dict(self) -> dict:
        return {"distribution": "lognormal", "mean": self.mean, "sigma": self.sigma}


class TruncatedNormal(Distribution):
    def __init__(self, mean: float, std: float, low: float, high: float):
        self.mean = _validate_finite(mean, "mean")
        self.std = _validate_finite(std, "std")
        self.low = _validate_finite(low, "low")
        self.high = _validate_finite(high, "high")
        if self.std <= 0:
            raise ValidationError("TruncatedNormal std must be greater than 0", "std", "> 0")
        if self.low >= self.high:
            raise ValidationError("TruncatedNormal low must be less than high", "low", "< high")

    def sample(self, n: int, seed: int | None = None) -> np.ndarray:
        _validate_sample_count(n)
        rng = np.random.default_rng(seed)
        accepted: list[np.ndarray] = []
        accepted_count = 0
        batch_size = max(n * 10, 100)
        max_draws = max(n * 1000, batch_size)
        draws = 0
        while accepted_count < n and draws < max_draws:
            samples = rng.normal(self.mean, self.std, batch_size)
            draws += batch_size
            samples = samples[(samples >= self.low) & (samples <= self.high)]
            if len(samples):
                accepted.append(samples)
                accepted_count += len(samples)
        if not accepted or accepted_count < n:
            raise ValueError("TruncatedNormal: too few samples in bounds")
        return np.concatenate(accepted)[:n]

    def to_dict(self) -> dict:
        return {
            "distribution": "truncated_normal",
            "mean": self.mean,
            "std": self.std,
            "low": self.low,
            "high": self.high,
        }

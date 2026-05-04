"""born_overlap is pure linear algebra — testable without lambeq."""

import numpy as np

from qrouter.retrieve import born_overlap


def test_overlap_self_is_one():
    v = np.array([0.6, 0.8], dtype=np.complex128)
    assert abs(born_overlap(v, v) - 1.0) < 1e-9


def test_overlap_orthogonal_is_zero():
    a = np.array([1.0, 0.0], dtype=np.complex128)
    b = np.array([0.0, 1.0], dtype=np.complex128)
    assert born_overlap(a, b) == 0.0


def test_overlap_known_small_case():
    # |+⟩ vs |0⟩ → |⟨+|0⟩|² = 1/2
    plus = np.array([1.0, 1.0], dtype=np.complex128) / np.sqrt(2)
    zero = np.array([1.0, 0.0], dtype=np.complex128)
    assert abs(born_overlap(plus, zero) - 0.5) < 1e-9


def test_overlap_complex_phase_is_modulus_squared():
    # |⟨a|b⟩|² should ignore overall phase
    a = np.array([1.0, 0.0], dtype=np.complex128)
    b = np.array([1j, 0.0],  dtype=np.complex128)
    assert abs(born_overlap(a, b) - 1.0) < 1e-9


def test_overlap_shape_mismatch_raises():
    a = np.array([1.0, 0.0],          dtype=np.complex128)
    b = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.complex128)
    try:
        born_overlap(a, b)
    except ValueError:
        return
    raise AssertionError("expected ValueError on shape mismatch")

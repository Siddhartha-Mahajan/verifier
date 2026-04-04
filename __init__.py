"""
CAISc 2026 Verifiable Problems -- Verification Module

Five problem verifiers, each exposing a verify() function that takes
(instance, submission) and returns a standardized result dict.
"""

__version__ = "1.0.0"

from helper.hadamard import verify as verify_hadamard
from helper.conway import verify as verify_conway
from helper.tensor import verify as verify_tensor
from helper.stilllife import verify as verify_stilllife
from helper.hpprotein import verify as verify_hpprotein

__all__ = [
    "verify_hadamard",
    "verify_conway",
    "verify_tensor",
    "verify_stilllife",
    "verify_hpprotein",
]

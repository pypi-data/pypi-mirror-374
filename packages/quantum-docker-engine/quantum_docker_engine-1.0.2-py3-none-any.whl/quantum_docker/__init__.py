"""
Quantum Docker Engine - A quantum computing-based container orchestration system.

This package provides quantum-enhanced container management using principles
from quantum mechanics like superposition, entanglement, and measurement.
"""

__version__ = "1.0.2"
__author__ = "Quantum Docker Team"

from .core.engine import QuantumDockerEngine
from .quantum.circuit_manager import QuantumCircuitManager
from .containers.quantum_container import QuantumContainer

__all__ = [
    "QuantumDockerEngine",
    "QuantumCircuitManager", 
    "QuantumContainer"
]

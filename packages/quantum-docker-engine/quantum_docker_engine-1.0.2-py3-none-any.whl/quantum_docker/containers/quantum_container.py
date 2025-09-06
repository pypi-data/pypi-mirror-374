import cirq
import numpy as np
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import uuid
import time
import json
from ..quantum.quantum_process_simulator import QuantumProcessSimulator
from ..quantum.quantum_error_correction import QuantumErrorCorrector


class ContainerState(Enum):
    """Quantum container states."""
    SUPERPOSITION = "superposition"
    RUNNING = "running" 
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    ENTANGLED = "entangled"
    MEASURED = "measured"
    ERROR_CORRECTED = "error_corrected"
    DECOHERENT = "decoherent"
    QUANTUM_TUNNELED = "quantum_tunneled"


@dataclass
class QuantumContainerConfig:
    """Configuration for quantum containers."""
    image: str
    name: str
    quantum_weight: float = 1.0
    entanglement_partners: List[str] = field(default_factory=list)
    superposition_states: List[str] = field(default_factory=lambda: ["running", "stopped", "suspended"])
    quantum_probability: float = 0.5
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    quantum_coherence_time: float = 5000.0  # milliseconds
    error_correction_enabled: bool = True
    quantum_tunneling_probability: float = 0.1
    entanglement_fidelity: float = 0.9


class QuantumContainer:
    """A container that exists in quantum superposition until measured."""
    
    def __init__(self, config: QuantumContainerConfig, circuit_manager):
        self.config = config
        self.container_id = str(uuid.uuid4())
        self.circuit_manager = circuit_manager
        
        # Quantum simulation components (NO traditional Docker!)
        self.quantum_process_simulator = QuantumProcessSimulator(config.image)
        self.quantum_error_corrector = QuantumErrorCorrector() if config.error_correction_enabled else None
        
        # Quantum states
        self.quantum_state = ContainerState.SUPERPOSITION
        self.state_amplitudes = {}
        self.entangled_containers = []
        self.measurement_history = []
        self.creation_time = time.time()
        self.last_coherence_check = time.time()
        # Optional classical/process identifier (used for display/persistence)
        # In pure-quantum mode we reuse the main quantum process id if/when running
        self.classical_container_id = None
        
        # Quantum resource allocation
        self.quantum_resources = {
            'cpu_qubits': [],
            'memory_qubits': [],
            'io_qubits': []
        }
        
        # Initialize quantum state amplitudes
        self._initialize_quantum_state()
        self._allocate_quantum_resources()
        
    def _allocate_quantum_resources(self):
        """Allocate quantum qubits for resource simulation."""
        # Allocate qubits for different resource types
        total_qubits_needed = 8  # 8 qubits per container
        
        start_qubit = len(self.circuit_manager.qubits) % 16
        self.quantum_resources = {
            'cpu_qubits': [start_qubit, start_qubit + 1, start_qubit + 2],
            'memory_qubits': [start_qubit + 3, start_qubit + 4, start_qubit + 5],
            'io_qubits': [start_qubit + 6, start_qubit + 7]
        }
        
        # Initialize resource states in superposition
        self._initialize_resource_superposition()
        
    def _initialize_quantum_state(self):
        """Initialize the quantum superposition state."""
        num_states = len(self.config.superposition_states)
        if num_states == 0:
            return
            
        # Equal superposition by default with quantum noise
        amplitude = 1.0 / np.sqrt(num_states)
        for state in self.config.superposition_states:
            # Add small quantum noise for realistic simulation
            noise = np.random.normal(0, 0.01)
            self.state_amplitudes[state] = complex(amplitude + noise, noise/10)
        
        # Normalize amplitudes
        total = sum(abs(amp)**2 for amp in self.state_amplitudes.values())
        for state in self.state_amplitudes:
            self.state_amplitudes[state] /= np.sqrt(total)
    
    async def create_superposition(self):
        """Put the container in quantum superposition."""
        if self.quantum_state != ContainerState.SUPERPOSITION:
            return
            
        # Create quantum circuit for this container
        qubit = cirq.LineQubit(0)
        circuit = cirq.Circuit()
        
        # Apply quantum gates based on configuration
        if self.config.quantum_probability != 0.5:
            # Custom probability using rotation gate
            angle = 2 * np.arccos(np.sqrt(self.config.quantum_probability))
            circuit.append(cirq.ry(angle)(qubit))
        else:
            # Equal superposition
            circuit.append(cirq.H(qubit))
            
        # Store the quantum circuit
        self.quantum_circuit = circuit
        
        print(f"Container {self.config.name} is now in quantum superposition")
        
    async def entangle_with(self, other_container: 'QuantumContainer'):
        """Create quantum entanglement with another container."""
        if other_container.container_id in [c.container_id for c in self.entangled_containers]:
            return  # Already entangled
            
        # Create entanglement circuit
        q1 = cirq.LineQubit(0)
        q2 = cirq.LineQubit(1)
        
        entanglement_circuit = cirq.Circuit()
        entanglement_circuit.append(cirq.H(q1))
        entanglement_circuit.append(cirq.CNOT(q1, q2))
        
        # Update both containers
        self.entangled_containers.append(other_container)
        other_container.entangled_containers.append(self)
        
        self.quantum_state = ContainerState.ENTANGLED
        other_container.quantum_state = ContainerState.ENTANGLED
        
        print(f"Containers {self.config.name} and {other_container.config.name} are now entangled")
        
    async def measure_state(self) -> str:
        """Perform quantum measurement to collapse the superposition."""
        if self.quantum_state == ContainerState.MEASURED:
            return self.measured_state
            
        # Simulate quantum measurement
        probabilities = [abs(amp)**2 for amp in self.state_amplitudes.values()]
        states = list(self.state_amplitudes.keys())
        
        # Quantum measurement collapse
        measured_state = np.random.choice(states, p=probabilities)
        self.measured_state = measured_state
        self.quantum_state = ContainerState.MEASURED
        
        # Record measurement
        self.measurement_history.append({
            'timestamp': time.time(),
            'measured_state': measured_state,
            'probabilities': dict(zip(states, probabilities))
        })
        
        # If entangled, affect partner containers
        for partner in self.entangled_containers:
            if partner.quantum_state != ContainerState.MEASURED:
                await partner._entangled_measurement_effect(measured_state)
        
        print(f"Container {self.config.name} measured in state: {measured_state}")
        return measured_state
    
    async def _entangled_measurement_effect(self, partner_state: str):
        """Handle the effect of measuring an entangled partner."""
        # Implement quantum correlation effects
        if partner_state == "running":
            # Entangled container tends to be in opposite state
            self.state_amplitudes["stopped"] = complex(0.8, 0)
            self.state_amplitudes["running"] = complex(0.6, 0)
        else:
            self.state_amplitudes["running"] = complex(0.8, 0)
            self.state_amplitudes["stopped"] = complex(0.6, 0)
            
        # Normalize amplitudes
        total = sum(abs(amp)**2 for amp in self.state_amplitudes.values())
        for state in self.state_amplitudes:
            self.state_amplitudes[state] /= np.sqrt(total)
    
    async def run(self) -> bool:
        """Run the quantum container using pure quantum simulation."""
        if self.quantum_state == ContainerState.SUPERPOSITION:
            measured_state = await self.measure_state()
        else:
            measured_state = getattr(self, 'measured_state', 'running')
            
        if measured_state == "running":
            try:
                # Pure quantum simulation - NO Docker containers!
                await self.quantum_process_simulator.create_quantum_process(
                    command=f"quantum_simulation_{self.config.image}",
                    process_id=f"main_{self.container_id[:8]}"
                )
                
                # Execute quantum process
                main_process_id = f"main_{self.container_id[:8]}"
                execution_success = await self.quantum_process_simulator.execute_quantum_process(main_process_id)
                
                if execution_success:
                    self.quantum_state = ContainerState.RUNNING
                    # Record process id for CLI display and persistence
                    self.classical_container_id = main_process_id
                    print(f" Quantum container {self.config.name} is now running in quantum simulation")
                    
                    # Start quantum error correction if enabled
                    if self.quantum_error_corrector:
                        asyncio.create_task(self._quantum_error_correction_loop())
                    
                    return True
                else:
                    print(f" Quantum process execution failed for {self.config.name}")
                    return False
                
            except Exception as e:
                print(f"Failed to run quantum container {self.config.name}: {e}")
                return False
        else:
            print(f"Container {self.config.name} measured in '{measured_state}' state - not starting")
            return False
    
    async def stop(self):
        """Stop the quantum container simulation."""
        try:
            # Stop quantum processes
            await self.quantum_process_simulator.terminate_all_processes()
            
            # Collapse quantum state to stopped
            self.quantum_state = ContainerState.STOPPED
            self.state_amplitudes = {"stopped": complex(1.0, 0.0)}
            
            print(f" Quantum container {self.config.name} stopped")
        except Exception as e:
            print(f"Failed to stop quantum container {self.config.name}: {e}")
    
    def get_quantum_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the quantum container."""
        # Clean state amplitudes for JSON serialization
        clean_amplitudes = {}
        for k, v in self.state_amplitudes.items():
            clean_amplitudes[k] = [float(v.real), float(v.imag)]
        
        # Clean measurement history
        clean_history = []
        for measurement in self.measurement_history:
            if isinstance(measurement, dict):
                clean_measurement = {}
                for mk, mv in measurement.items():
                    if isinstance(mv, (str, int, float, bool, type(None))):
                        clean_measurement[mk] = mv
                    else:
                        clean_measurement[mk] = str(mv)
                clean_history.append(clean_measurement)
            else:
                clean_history.append(str(measurement))
        
        quantum_info = {
            'container_id': self.container_id,
            'name': self.config.name,
            'image': self.config.image,
            'quantum_weight': float(self.config.quantum_weight),
            'quantum_probability': float(self.config.quantum_probability),
            'superposition_states': list(self.config.superposition_states),
            'quantum_state': self.quantum_state.value,
            'state_amplitudes': clean_amplitudes,
            'entangled_partners': [c.config.name for c in self.entangled_containers],
            'measurement_history': clean_history,
            'creation_time': float(self.creation_time),
            'coherence_time': float(self.config.quantum_coherence_time),
            'error_correction_enabled': bool(self.config.error_correction_enabled),
            # Use stored classical/process id if available; remains None otherwise
            'classical_container_id': getattr(self, 'classical_container_id', None)
        }
        
        # Add quantum process information
        if hasattr(self, 'quantum_process_simulator'):
            quantum_info['quantum_processes'] = self.quantum_process_simulator.get_all_processes_status()
        
        # Add error correction stats
        if self.quantum_error_corrector:
            quantum_info['error_correction_stats'] = self.quantum_error_corrector.get_error_correction_stats()
        
        return quantum_info
    
    def apply_quantum_gate(self, gate_type: str, **params):
        """Apply quantum gates to modify the container's quantum state."""
        if self.quantum_state != ContainerState.SUPERPOSITION:
            print(f"Cannot apply quantum gate to container in {self.quantum_state.value} state")
            return
            
        if gate_type == "X":
            # Pauli-X gate (quantum NOT)
            new_amplitudes = {}
            states = list(self.state_amplitudes.keys())
            if len(states) == 2:
                new_amplitudes[states[0]] = self.state_amplitudes[states[1]]
                new_amplitudes[states[1]] = self.state_amplitudes[states[0]]
                self.state_amplitudes = new_amplitudes
                
        elif gate_type == "Z":
            # Pauli-Z gate (phase flip)
            for i, (state, amplitude) in enumerate(self.state_amplitudes.items()):
                if i % 2 == 1:
                    self.state_amplitudes[state] = -amplitude
                    
        elif gate_type == "RY":
            # Rotation around Y-axis
            angle = params.get('angle', np.pi/4)
            states = list(self.state_amplitudes.keys())
            if len(states) == 2:
                cos_half = np.cos(angle/2)
                sin_half = np.sin(angle/2)
                
                old_0 = self.state_amplitudes[states[0]]
                old_1 = self.state_amplitudes[states[1]]
                
                self.state_amplitudes[states[0]] = cos_half * old_0 - sin_half * old_1
                self.state_amplitudes[states[1]] = sin_half * old_0 + cos_half * old_1
        
        print(f"Applied {gate_type} gate to container {self.config.name}")
    
    def _initialize_resource_superposition(self):
        """Initialize quantum resource states in superposition."""
        # CPU utilization in superposition
        cpu_circuit = cirq.Circuit()
        for qubit_idx in self.quantum_resources['cpu_qubits']:
            qubit = cirq.LineQubit(qubit_idx)
            cpu_circuit.append(cirq.H(qubit))  # Equal superposition
        
        # Memory allocation in superposition  
        memory_circuit = cirq.Circuit()
        for qubit_idx in self.quantum_resources['memory_qubits']:
            qubit = cirq.LineQubit(qubit_idx)
            memory_circuit.append(cirq.H(qubit))
        
        # I/O operations in superposition
        io_circuit = cirq.Circuit()
        for qubit_idx in self.quantum_resources['io_qubits']:
            qubit = cirq.LineQubit(qubit_idx)
            io_circuit.append(cirq.H(qubit))
    
    async def _quantum_error_correction_loop(self):
        """Continuous quantum error correction loop."""
        while self.quantum_state == ContainerState.RUNNING:
            try:
                # Check for quantum decoherence
                time_since_creation = time.time() - self.creation_time
                if time_since_creation * 1000 > self.config.quantum_coherence_time:
                    await self._handle_decoherence()
                
                # Run error correction cycle
                if self.quantum_error_corrector:
                    quantum_state_array = self._get_current_quantum_state_array()
                    correction_stats = await self.quantum_error_corrector.run_error_correction_cycle(quantum_state_array)
                    
                    # Log errors if found
                    if correction_stats['detected_errors'] > 0:
                        print(f"  Container {self.config.name}: {correction_stats['detected_errors']} quantum errors corrected")
                
                # Sleep before next correction cycle
                await asyncio.sleep(0.1)  # 100ms correction cycle
                
            except Exception as e:
                print(f"Error correction loop failed for {self.config.name}: {e}")
                break
    
    def _get_current_quantum_state_array(self) -> np.ndarray:
        """Get current quantum state as numpy array for error correction."""
        # Convert state amplitudes to quantum state vector
        num_states = len(self.state_amplitudes)
        state_vector = np.zeros(2**3)  # 3 qubits for basic states
        
        for i, (state, amplitude) in enumerate(self.state_amplitudes.items()):
            if i < len(state_vector):
                state_vector[i] = amplitude
        
        # Normalize
        norm = np.linalg.norm(state_vector)
        if norm > 0:
            state_vector /= norm
            
        return state_vector
    
    async def _handle_decoherence(self):
        """Handle quantum decoherence by refreshing quantum state."""
        print(f" Handling decoherence for container {self.config.name}")
        
        self.quantum_state = ContainerState.DECOHERENT
        
        # Inject decoherence errors if error correction is enabled
        if self.quantum_error_corrector:
            decoherence_errors = self.quantum_error_corrector.simulate_decoherence(decoherence_rate=0.05)
            
            # Attempt to correct decoherence
            for error in decoherence_errors:
                await self.quantum_error_corrector.correct_quantum_error(error)
        
        # Refresh quantum state
        self._initialize_quantum_state()
        self.last_coherence_check = time.time()
        self.quantum_state = ContainerState.RUNNING
    
    async def quantum_tunnel_to_state(self, target_state: str) -> bool:
        """Use quantum tunneling to change container state."""
        if target_state not in self.config.superposition_states:
            print(f" Invalid target state: {target_state}")
            return False
        
        # Enhanced quantum tunneling with better probability calculation
        current_amplitude = self.state_amplitudes.get(target_state, complex(0, 0))
        current_probability = abs(current_amplitude)**2
        
        # Enhanced tunneling probability - higher chance for demonstration
        base_probability = self.config.quantum_tunneling_probability
        enhancement_factor = 1.5  # Increase tunneling success rate
        barrier_height = 1.0 - current_probability  # Energy barrier to overcome
        
        # Quantum tunneling probability using enhanced model
        tunneling_probability = min(0.8, base_probability * enhancement_factor * (1 + barrier_height))
        
        print(f" Attempting quantum tunneling for {self.config.name} to state '{target_state}'")
        print(f" Tunneling probability: {tunneling_probability:.3f}")
        
        if np.random.random() < tunneling_probability:
            # Successful quantum tunneling - transition to target state
            self.state_amplitudes = {state: complex(0, 0) for state in self.state_amplitudes}
            self.state_amplitudes[target_state] = complex(1.0, 0)
            
            # Update quantum state
            if target_state == "running":
                self.quantum_state = ContainerState.RUNNING
            elif target_state == "stopped":
                self.quantum_state = ContainerState.STOPPED
            elif target_state == "suspended":
                self.quantum_state = ContainerState.SUSPENDED
            else:
                self.quantum_state = ContainerState.QUANTUM_TUNNELED
            
            print(f" Quantum tunneling successful: {self.config.name} -> {target_state}")
            return True
        else:
            print(f" Quantum tunneling failed: {self.config.name} - barrier too high")
            return False
    
    async def apply_quantum_superposition_evolution(self, evolution_time: float):
        """Apply time evolution to quantum superposition states."""
        # Simulate quantum time evolution using Schrödinger equation
        hamiltonian_strength = 0.1  # Weak Hamiltonian for slow evolution
        
        for state, amplitude in self.state_amplitudes.items():
            # Apply phase evolution
            phase_evolution = np.exp(-1j * hamiltonian_strength * evolution_time)
            self.state_amplitudes[state] = amplitude * phase_evolution
        
        print(f"  Applied quantum evolution for {evolution_time:.2f}s to {self.config.name}")
    
    async def create_quantum_checkpoint(self) -> str:
        """Create a quantum checkpoint of current container state."""
        checkpoint_id = f"checkpoint_{self.container_id[:8]}_{int(time.time())}"
        
        checkpoint_data = {
            'container_id': self.container_id,
            'quantum_state': self.quantum_state.value,
            'state_amplitudes': {k: [v.real, v.imag] for k, v in self.state_amplitudes.items()},
            'quantum_resources': self.quantum_resources,
            'measurement_history': self.measurement_history,
            'timestamp': time.time()
        }
        
        # Add process state if available
        if hasattr(self, 'quantum_process_simulator'):
            checkpoint_data['process_state'] = self.quantum_process_simulator.get_all_processes_status()
        
        # Store checkpoint (in real implementation, this would be persisted)
        if not hasattr(self, 'quantum_checkpoints'):
            self.quantum_checkpoints = {}
        self.quantum_checkpoints[checkpoint_id] = checkpoint_data
        
        print(f" Quantum checkpoint created: {checkpoint_id}")
        return checkpoint_id
    
    async def restore_quantum_checkpoint(self, checkpoint_id: str) -> bool:
        """Restore container from a quantum checkpoint."""
        if not hasattr(self, 'quantum_checkpoints') or checkpoint_id not in self.quantum_checkpoints:
            print(f" Checkpoint not found: {checkpoint_id}")
            return False
        
        try:
            checkpoint_data = self.quantum_checkpoints[checkpoint_id]
            
            # Restore quantum state
            self.quantum_state = ContainerState[checkpoint_data['quantum_state'].upper()]
            
            # Restore state amplitudes
            self.state_amplitudes = {}
            for state, amplitude_parts in checkpoint_data['state_amplitudes'].items():
                self.state_amplitudes[state] = complex(amplitude_parts[0], amplitude_parts[1])
            
            # Restore other quantum properties
            self.quantum_resources = checkpoint_data['quantum_resources']
            self.measurement_history = checkpoint_data['measurement_history']
            
            print(f"📼 Quantum checkpoint restored: {checkpoint_id}")
            return True
            
        except Exception as e:
            print(f"Failed to restore checkpoint {checkpoint_id}: {e}")
            return False
    
    def get_quantum_entanglement_strength(self, other_container: 'QuantumContainer') -> float:
        """Calculate quantum entanglement strength with another container."""
        if other_container not in self.entangled_containers:
            return 0.0
        
        # Calculate entanglement based on state correlation
        correlation = 0.0
        for state in self.state_amplitudes:
            if state in other_container.state_amplitudes:
                self_amp = self.state_amplitudes[state]
                other_amp = other_container.state_amplitudes[state]
                correlation += (self_amp * np.conj(other_amp)).real
        
        entanglement_strength = abs(correlation) * self.config.entanglement_fidelity
        return min(entanglement_strength, 1.0)
    
    async def perform_quantum_annealing_optimization(self) -> Dict[str, Any]:
        """Optimize container parameters using quantum annealing."""
        if self.quantum_error_corrector:
            return await self.quantum_error_corrector.perform_quantum_annealing_correction()
        else:
            print(" Quantum error corrector not available for annealing")
            return {}


class QuantumContainerOrchestrator:
    """Orchestrates multiple quantum containers."""
    
    def __init__(self, circuit_manager):
        self.circuit_manager = circuit_manager
        self.containers: Dict[str, QuantumContainer] = {}
        
    async def create_container(self, config: QuantumContainerConfig) -> QuantumContainer:
        """Create a new quantum container."""
        container = QuantumContainer(config, self.circuit_manager)
        await container.create_superposition()
        self.containers[container.container_id] = container
        return container
    
    async def create_entangled_cluster(self, container_configs: List[QuantumContainerConfig]) -> List[QuantumContainer]:
        """Create a cluster of entangled containers."""
        containers = []
        
        # Create all containers first
        for config in container_configs:
            container = await self.create_container(config)
            containers.append(container)
            
        # Create entanglement between all pairs
        for i in range(len(containers)):
            for j in range(i + 1, len(containers)):
                await containers[i].entangle_with(containers[j])
                
        return containers
    
    async def quantum_load_balance(self, container_names: List[str], nodes: List[str]) -> Dict[str, str]:
        """Use quantum algorithm to load balance containers across nodes."""
        return self.circuit_manager.quantum_scheduling_algorithm(container_names, nodes)
    
    def get_cluster_state(self) -> Dict[str, Any]:
        """Get the quantum state of all containers."""
        return {
            'total_containers': len(self.containers),
            'containers': {
                cid: container.get_quantum_info() 
                for cid, container in self.containers.items()
            }
        }

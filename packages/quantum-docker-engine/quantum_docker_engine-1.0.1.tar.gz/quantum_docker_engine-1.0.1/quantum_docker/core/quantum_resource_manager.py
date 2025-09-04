import cirq
import numpy as np
import psutil
import docker
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
import math


class ResourceType(Enum):
    """Types of resources that can be managed quantumly."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    GPU = "gpu"


@dataclass
class QuantumResourceState:
    """Represents the quantum state of a resource."""
    resource_type: ResourceType
    total_capacity: float
    available_capacity: float
    quantum_probability: float
    entanglement_factor: float
    measurement_uncertainty: float


@dataclass
class ResourceAllocation:
    """Represents a resource allocation decision."""
    container_id: str
    node_id: str
    resource_type: ResourceType
    allocated_amount: float
    quantum_confidence: float
    allocation_timestamp: float


class QuantumResourceManager:
    """Manages resources using quantum measurement and superposition."""
    
    def __init__(self, circuit_manager, num_qubits: int = 12):
        self.circuit_manager = circuit_manager
        self.num_qubits = num_qubits
        self.qubits = cirq.LineQubit.range(num_qubits)
        self.simulator = cirq.Simulator()
        
        # Resource tracking
        self.resource_states: Dict[str, Dict[ResourceType, QuantumResourceState]] = {}
        self.allocation_history: List[ResourceAllocation] = []
        self.quantum_scheduler_circuit = None
        
        # Pure quantum simulation mode - no Docker required
        self.docker_client = None  # Disabled for pure quantum simulation
        
    async def initialize_quantum_resources(self, node_ids: List[str]):
        """Initialize quantum resource states for all nodes."""
        for node_id in node_ids:
            await self._create_node_quantum_state(node_id)
    
    async def _create_node_quantum_state(self, node_id: str):
        """Create quantum superposition state for a node's resources."""
        # Get actual system resources
        cpu_count = psutil.cpu_count()
        memory_total = psutil.virtual_memory().total / (1024**3)  # GB
        disk_total = psutil.disk_usage('/').total / (1024**3)  # GB
        
        # Create quantum resource states
        self.resource_states[node_id] = {
            ResourceType.CPU: QuantumResourceState(
                resource_type=ResourceType.CPU,
                total_capacity=float(cpu_count),
                available_capacity=float(cpu_count),
                quantum_probability=1.0,
                entanglement_factor=0.0,
                measurement_uncertainty=0.1
            ),
            ResourceType.MEMORY: QuantumResourceState(
                resource_type=ResourceType.MEMORY,
                total_capacity=memory_total,
                available_capacity=memory_total,
                quantum_probability=1.0,
                entanglement_factor=0.0,
                measurement_uncertainty=0.05
            ),
            ResourceType.STORAGE: QuantumResourceState(
                resource_type=ResourceType.STORAGE,
                total_capacity=disk_total,
                available_capacity=disk_total,
                quantum_probability=1.0,
                entanglement_factor=0.0,
                measurement_uncertainty=0.02
            )
        }
        
        # Create quantum circuit for this node's resources
        await self._create_resource_superposition_circuit(node_id)
        
    async def _create_resource_superposition_circuit(self, node_id: str):
        """Create quantum circuit representing resource superposition."""
        circuit = cirq.Circuit()
        
        # Use 3 qubits per resource type (CPU, Memory, Storage)
        resource_qubits = self.qubits[:9]  # 3 resources × 3 qubits each
        
        # Create superposition for each resource
        for i, resource_type in enumerate([ResourceType.CPU, ResourceType.MEMORY, ResourceType.STORAGE]):
            resource_qubit_start = i * 3
            resource_qubit_end = (i + 1) * 3
            
            # Put resource qubits in superposition
            for j in range(resource_qubit_start, resource_qubit_end):
                circuit.append(cirq.H(self.qubits[j]))
            
            # Add entanglement between resource qubits
            for j in range(resource_qubit_start, resource_qubit_end - 1):
                circuit.append(cirq.CNOT(self.qubits[j], self.qubits[j + 1]))
        
        # Store circuit for this node
        setattr(self, f'_circuit_{node_id}', circuit)
    
    async def quantum_resource_allocation(self, 
                                        container_requirements: Dict[str, Dict[ResourceType, float]], 
                                        available_nodes: List[str]) -> Dict[str, str]:
        """Use quantum algorithms to optimally allocate containers to nodes."""
        
        if not container_requirements or not available_nodes:
            return {}
        
        # Create quantum optimization circuit
        allocation_circuit = await self._create_allocation_circuit(container_requirements, available_nodes)
        
        # Measure quantum state to get allocation decisions
        allocation_probabilities = await self._measure_allocation_circuit(allocation_circuit)
        
        # Interpret quantum measurements as allocation decisions
        allocations = self._interpret_quantum_allocations(
            allocation_probabilities, 
            list(container_requirements.keys()), 
            available_nodes
        )
        
        # Apply allocations and update resource states
        for container_id, node_id in allocations.items():
            await self._apply_quantum_allocation(container_id, node_id, container_requirements[container_id])
        
        return allocations
    
    async def _create_allocation_circuit(self, 
                                       container_requirements: Dict[str, Dict[ResourceType, float]], 
                                       available_nodes: List[str]) -> cirq.Circuit:
        """Create quantum circuit for container-node allocation optimization."""
        
        circuit = cirq.Circuit()
        num_containers = len(container_requirements)
        num_nodes = len(available_nodes)
        
        # Use qubits to represent container-node mappings
        qubits_needed = num_containers * num_nodes
        if qubits_needed > self.num_qubits:
            raise ValueError(f"Need {qubits_needed} qubits but only have {self.num_qubits}")
        
        allocation_qubits = self.qubits[:qubits_needed]
        
        # Initialize superposition for all possible allocations
        for qubit in allocation_qubits:
            circuit.append(cirq.H(qubit))
        
        # Apply quantum cost function based on resource requirements
        container_list = list(container_requirements.keys())
        for i, container_id in enumerate(container_list):
            for j, node_id in enumerate(available_nodes):
                qubit_index = i * num_nodes + j
                if qubit_index < len(allocation_qubits):
                    # Apply rotation based on resource fit
                    fit_score = await self._calculate_resource_fit(container_id, node_id, container_requirements[container_id])
                    rotation_angle = fit_score * np.pi / 2
                    circuit.append(cirq.ry(rotation_angle)(allocation_qubits[qubit_index]))
        
        # Add entanglement between related allocations
        for i in range(0, len(allocation_qubits) - 1, 2):
            if i + 1 < len(allocation_qubits):
                circuit.append(cirq.CNOT(allocation_qubits[i], allocation_qubits[i + 1]))
        
        return circuit
    
    async def _calculate_resource_fit(self, container_id: str, node_id: str, requirements: Dict[ResourceType, float]) -> float:
        """Calculate how well a container fits on a node (0.0 to 1.0)."""
        if node_id not in self.resource_states:
            return 0.0
        
        fit_scores = []
        node_resources = self.resource_states[node_id]
        
        for resource_type, required_amount in requirements.items():
            if resource_type in node_resources:
                available = node_resources[resource_type].available_capacity
                if available >= required_amount:
                    # Higher score for better resource availability
                    utilization = required_amount / node_resources[resource_type].total_capacity
                    fit_score = 1.0 - utilization  # Prefer lower utilization
                    fit_scores.append(fit_score)
                else:
                    fit_scores.append(0.0)  # Cannot fit
            else:
                fit_scores.append(0.5)  # Unknown resource type
        
        return np.mean(fit_scores) if fit_scores else 0.0
    
    async def _measure_allocation_circuit(self, circuit: cirq.Circuit) -> Dict[str, float]:
        """Measure the allocation circuit and return probabilities."""
        # Add measurements
        measurement_circuit = circuit.copy()
        measurement_circuit.append(cirq.measure(*self.qubits[:len([op for op in circuit.all_qubits()])], key='allocation'))
        
        # Run quantum simulation
        result = self.simulator.run(measurement_circuit, repetitions=1000)
        measurements = result.measurements['allocation']
        
        # Calculate state probabilities
        state_counts = {}
        for measurement in measurements:
            state = ''.join(map(str, measurement))
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Convert to probabilities
        total = len(measurements)
        probabilities = {state: count / total for state, count in state_counts.items()}
        
        return probabilities
    
    def _interpret_quantum_allocations(self, 
                                     probabilities: Dict[str, float], 
                                     container_ids: List[str], 
                                     node_ids: List[str]) -> Dict[str, str]:
        """Interpret quantum measurement results as container-node allocations."""
        allocations = {}
        num_nodes = len(node_ids)
        
        for container_idx, container_id in enumerate(container_ids):
            best_node = node_ids[0]
            best_probability = 0.0
            
            # Find the node with highest quantum probability for this container
            for node_idx, node_id in enumerate(node_ids):
                qubit_position = container_idx * num_nodes + node_idx
                
                # Sum probabilities where this container-node bit is 1
                total_prob = 0.0
                count = 0
                
                for state, prob in probabilities.items():
                    if qubit_position < len(state) and state[qubit_position] == '1':
                        total_prob += prob
                        count += 1
                
                avg_prob = total_prob / max(count, 1)
                
                if avg_prob > best_probability:
                    best_probability = avg_prob
                    best_node = node_id
            
            allocations[container_id] = best_node
        
        return allocations
    
    async def _apply_quantum_allocation(self, container_id: str, node_id: str, requirements: Dict[ResourceType, float]):
        """Apply the quantum allocation decision and update resource states."""
        if node_id not in self.resource_states:
            return
        
        node_resources = self.resource_states[node_id]
        quantum_confidence = 0.8  # Base confidence level
        
        for resource_type, required_amount in requirements.items():
            if resource_type in node_resources:
                resource_state = node_resources[resource_type]
                
                # Apply quantum uncertainty to allocation
                uncertainty = resource_state.measurement_uncertainty
                actual_allocation = required_amount * (1 + np.random.normal(0, uncertainty))
                
                # Update available capacity
                resource_state.available_capacity = max(0, resource_state.available_capacity - actual_allocation)
                
                # Update quantum probability based on remaining resources
                utilization = (resource_state.total_capacity - resource_state.available_capacity) / resource_state.total_capacity
                resource_state.quantum_probability = 1.0 - utilization
                
                # Record allocation
                allocation = ResourceAllocation(
                    container_id=container_id,
                    node_id=node_id,
                    resource_type=resource_type,
                    allocated_amount=actual_allocation,
                    quantum_confidence=quantum_confidence,
                    allocation_timestamp=time.time()
                )
                self.allocation_history.append(allocation)
        
        print(f"Quantum allocation: Container {container_id[:8]} -> Node {node_id} (confidence: {quantum_confidence:.2f})")
    
    async def quantum_resource_measurement(self, node_id: str) -> Dict[ResourceType, float]:
        """Perform quantum measurement to get current resource states."""
        if node_id not in self.resource_states:
            return {}
        
        # Create measurement circuit for this node
        circuit_attr = f'_circuit_{node_id}'
        if not hasattr(self, circuit_attr):
            await self._create_resource_superposition_circuit(node_id)
        
        circuit = getattr(self, circuit_attr)
        measurement_circuit = circuit.copy()
        measurement_circuit.append(cirq.measure(*self.qubits[:9], key='resources'))
        
        # Perform quantum measurement
        result = self.simulator.run(measurement_circuit, repetitions=100)
        measurements = result.measurements['resources']
        
        # Interpret measurements as resource availability
        resource_measurements = {}
        for i, resource_type in enumerate([ResourceType.CPU, ResourceType.MEMORY, ResourceType.STORAGE]):
            # Extract bits for this resource (3 bits per resource)
            resource_bits = measurements[:, i*3:(i+1)*3]
            
            # Calculate average measurement value
            resource_values = []
            for bits in resource_bits:
                # Convert 3-bit measurement to resource percentage
                bit_value = int(''.join(map(str, bits)), 2)
                resource_percent = bit_value / 7.0  # 3 bits = 0-7 range
                resource_values.append(resource_percent)
            
            avg_resource = np.mean(resource_values)
            resource_measurements[resource_type] = avg_resource
        
        return resource_measurements
    
    async def quantum_load_rebalancing(self, node_ids: List[str]) -> Dict[str, List[str]]:
        """Use quantum algorithms to rebalance container loads across nodes."""
        rebalancing_plan = {node_id: [] for node_id in node_ids}
        
        # Measure current resource states
        node_states = {}
        for node_id in node_ids:
            node_states[node_id] = await self.quantum_resource_measurement(node_id)
        
        # Create quantum circuit for load balancing optimization
        circuit = cirq.Circuit()
        
        # Use quantum annealing approach for optimization
        num_nodes = len(node_ids)
        balance_qubits = self.qubits[:num_nodes]
        
        # Initialize in superposition
        for qubit in balance_qubits:
            circuit.append(cirq.H(qubit))
        
        # Apply cost function for load imbalance
        for i, node_id in enumerate(node_ids):
            load_factor = self._calculate_node_load(node_id)
            # Higher load = more rotation (higher energy state)
            rotation_angle = load_factor * np.pi
            circuit.append(cirq.ry(rotation_angle)(balance_qubits[i]))
        
        # Add entanglement for collective optimization
        for i in range(num_nodes - 1):
            circuit.append(cirq.CNOT(balance_qubits[i], balance_qubits[i + 1]))
        
        # Measure for rebalancing decisions
        circuit.append(cirq.measure(*balance_qubits, key='rebalance'))
        result = self.simulator.run(circuit, repetitions=500)
        
        # Interpret results as rebalancing instructions
        measurements = result.measurements['rebalance']
        avg_measurements = np.mean(measurements, axis=0)
        
        # Generate rebalancing plan based on quantum measurements
        for i, node_id in enumerate(node_ids):
            if avg_measurements[i] > 0.6:  # High quantum energy = needs rebalancing
                rebalancing_plan[node_id] = self._get_containers_to_migrate(node_id)
        
        return rebalancing_plan
    
    def _calculate_node_load(self, node_id: str) -> float:
        """Calculate current load factor for a node (0.0 to 1.0)."""
        if node_id not in self.resource_states:
            return 0.0
        
        load_factors = []
        for resource_state in self.resource_states[node_id].values():
            utilization = (resource_state.total_capacity - resource_state.available_capacity) / resource_state.total_capacity
            load_factors.append(utilization)
        
        return np.mean(load_factors) if load_factors else 0.0
    
    def _get_containers_to_migrate(self, node_id: str) -> List[str]:
        """Get list of containers that should be migrated from overloaded node."""
        # In a real implementation, this would query running containers
        # For now, return containers from recent allocations
        containers_on_node = []
        for allocation in reversed(self.allocation_history[-20:]):  # Last 20 allocations
            if allocation.node_id == node_id and allocation.container_id not in containers_on_node:
                containers_on_node.append(allocation.container_id)
                if len(containers_on_node) >= 3:  # Limit migrations
                    break
        
        return containers_on_node
    
    def get_quantum_resource_status(self) -> Dict[str, Any]:
        """Get comprehensive status of quantum resource management."""
        status = {
            'nodes': {},
            'total_allocations': len(self.allocation_history),
            'quantum_coherence': self._calculate_system_coherence(),
            'resource_entanglement': self._calculate_resource_entanglement()
        }
        
        for node_id, resources in self.resource_states.items():
            node_status = {
                'load_factor': self._calculate_node_load(node_id),
                'resources': {}
            }
            
            for resource_type, resource_state in resources.items():
                node_status['resources'][resource_type.value] = {
                    'total': resource_state.total_capacity,
                    'available': resource_state.available_capacity,
                    'utilization': (resource_state.total_capacity - resource_state.available_capacity) / resource_state.total_capacity,
                    'quantum_probability': resource_state.quantum_probability,
                    'measurement_uncertainty': resource_state.measurement_uncertainty
                }
            
            status['nodes'][node_id] = node_status
        
        return status
    
    def _calculate_system_coherence(self) -> float:
        """Calculate overall quantum coherence of the resource system."""
        if not self.resource_states:
            return 0.0
        
        coherence_values = []
        for resources in self.resource_states.values():
            for resource_state in resources.values():
                coherence_values.append(resource_state.quantum_probability)
        
        return np.mean(coherence_values) if coherence_values else 0.0
    
    def _calculate_resource_entanglement(self) -> float:
        """Calculate the level of resource entanglement across the system."""
        if not self.resource_states:
            return 0.0
        
        entanglement_values = []
        for resources in self.resource_states.values():
            for resource_state in resources.values():
                entanglement_values.append(resource_state.entanglement_factor)
        
        return np.mean(entanglement_values) if entanglement_values else 0.0
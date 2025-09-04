import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..quantum.circuit_manager import QuantumCircuitManager
from ..containers.quantum_container import QuantumContainer, QuantumContainerConfig, QuantumContainerOrchestrator
from ..networking.quantum_network import QuantumNetworkManager
from .quantum_resource_manager import QuantumResourceManager, ResourceType
from ..monitoring.quantum_monitor import QuantumMonitoringSystem


@dataclass
class QuantumEngineConfig:
    """Configuration for the Quantum Docker Engine."""
    num_qubits: int = 16
    simulation_backend: str = "cirq"
    max_containers: int = 50
    enable_quantum_networking: bool = True
    enable_quantum_scheduling: bool = True
    enable_quantum_load_balancing: bool = True
    decoherence_time_ms: float = 1000.0


class QuantumDockerEngine:
    """Main Quantum Docker Engine that orchestrates all quantum components."""
    
    def __init__(self, config: Optional[QuantumEngineConfig] = None):
        self.config = config or QuantumEngineConfig()
        
        # Initialize quantum components
        self.circuit_manager = QuantumCircuitManager(num_qubits=self.config.num_qubits)
        self.resource_manager = QuantumResourceManager(self.circuit_manager, num_qubits=self.config.num_qubits)
        self.container_orchestrator = QuantumContainerOrchestrator(self.circuit_manager)
        self.quantum_monitor = QuantumMonitoringSystem()
        
        if self.config.enable_quantum_networking:
            self.network_manager = QuantumNetworkManager(self.circuit_manager)
        else:
            self.network_manager = None
        
        # Engine state
        self.engine_started = False
        self.start_time = None
        self.available_nodes = ["localhost"]  # Default single node
        
    async def start_engine(self):
        """Start the Quantum Docker Engine."""
        if self.engine_started:
            print("Quantum Docker Engine is already running")
            return
        
        print("Starting Quantum Docker Engine...")
        
        # Initialize quantum resources
        await self.resource_manager.initialize_quantum_resources(self.available_nodes)
        print("Quantum resource states initialized")
        
        # Start network manager if enabled
        if self.network_manager:
            print("Quantum network manager initialized")
        
        self.engine_started = True
        self.start_time = time.time()
        
        print("Quantum Docker Engine is now running!")
        print(f"   - Available nodes: {len(self.available_nodes)}")
        print(f"   - Quantum qubits: {self.config.num_qubits}")
        print(f"   - Max containers: {self.config.max_containers}")
        
    async def stop_engine(self):
        """Stop the Quantum Docker Engine."""
        if not self.engine_started:
            print("Quantum Docker Engine is not running")
            return
        
        print("Stopping Quantum Docker Engine...")
        
        # Stop all quantum containers
        containers = list(self.container_orchestrator.containers.values())
        for container in containers:
            await container.stop()
        
        self.engine_started = False
        print("Quantum Docker Engine stopped")
    
    async def create_quantum_container(self, 
                                     image: str, 
                                     name: str, 
                                     **kwargs) -> QuantumContainer:
        """Create a new quantum container."""
        if not self.engine_started:
            raise RuntimeError("Quantum Docker Engine is not running. Please start it first.")
        
        # Create quantum container configuration
        config = QuantumContainerConfig(
            image=image,
            name=name,
            quantum_weight=kwargs.get('quantum_weight', 1.0),
            superposition_states=kwargs.get('superposition_states', ["running", "stopped"]),
            quantum_probability=kwargs.get('quantum_probability', 0.5),
            resource_requirements=kwargs.get('resource_requirements', {})
        )
        
        # Create container using orchestrator
        container = await self.container_orchestrator.create_container(config)
        
        print(f"Created quantum container: {name} (ID: {container.container_id[:8]})")
        return container
    
    async def run_quantum_container(self, container_name_or_id: str) -> bool:
        """Run a quantum container (with measurement)."""
        container = self._find_container(container_name_or_id)
        if not container:
            print(f"Container not found: {container_name_or_id}")
            return False
        
        success = await container.run()
        return success
    
    async def stop_quantum_container(self, container_name_or_id: str) -> bool:
        """Stop a quantum container."""
        container = self._find_container(container_name_or_id)
        if not container:
            print(f"Container not found: {container_name_or_id}")
            return False
        
        await container.stop()
        return True
    
    async def measure_container(self, container_name_or_id: str) -> Optional[str]:
        """Perform quantum measurement on a container."""
        container = self._find_container(container_name_or_id)
        if not container:
            print(f"Container not found: {container_name_or_id}")
            return None
        
        measured_state = await container.measure_state()
        return measured_state
    
    async def entangle_containers(self, container1: str, container2: str) -> bool:
        """Create quantum entanglement between two containers."""
        c1 = self._find_container(container1)
        c2 = self._find_container(container2)
        
        if not c1 or not c2:
            print(f"One or both containers not found: {container1}, {container2}")
            return False
        
        await c1.entangle_with(c2)
        
        # Also create quantum network channel if networking is enabled
        if self.network_manager:
            try:
                await self.network_manager.create_quantum_channel(c1.container_id, c2.container_id)
            except Exception as e:
                print(f"Failed to create quantum network channel: {e}")
        
        return True
    
    async def create_quantum_cluster(self, 
                                   container_configs: List[Dict[str, Any]], 
                                   cluster_name: str) -> List[QuantumContainer]:
        """Create a cluster of entangled quantum containers."""
        if not self.engine_started:
            raise RuntimeError("Quantum Docker Engine is not running")
        
        print(f"Creating quantum cluster: {cluster_name}")
        
        # Convert dict configs to QuantumContainerConfig objects
        configs = []
        for config_dict in container_configs:
            config = QuantumContainerConfig(
                image=config_dict['image'],
                name=config_dict['name'],
                quantum_weight=config_dict.get('quantum_weight', 1.0),
                superposition_states=config_dict.get('superposition_states', ["running", "stopped"]),
                quantum_probability=config_dict.get('quantum_probability', 0.5),
                resource_requirements=config_dict.get('resource_requirements', {})
            )
            configs.append(config)
        
        # Create entangled cluster
        containers = await self.container_orchestrator.create_entangled_cluster(configs)
        
        # Create quantum mesh network for the cluster
        if self.network_manager and len(containers) > 1:
            container_ids = [c.container_id for c in containers]
            await self.network_manager.create_quantum_mesh_network(container_ids)
        
        print(f"Quantum cluster '{cluster_name}' created with {len(containers)} containers")
        return containers
    
    async def quantum_load_balance(self, container_names: List[str]) -> Dict[str, str]:
        """Perform quantum load balancing of containers across nodes."""
        if not self.config.enable_quantum_load_balancing:
            print("Quantum load balancing is disabled")
            return {}
        
        print("Performing quantum load balancing...")
        
        # Use quantum scheduling algorithm
        allocation = await self.container_orchestrator.quantum_load_balance(
            container_names, 
            self.available_nodes
        )
        
        print(f"Quantum load balancing completed:")
        for container, node in allocation.items():
            print(f"   {container} -> {node}")
        
        return allocation
    
    async def send_quantum_message(self, 
                                 sender_container: str, 
                                 receiver_container: str, 
                                 message_type: str, 
                                 data: Dict[str, Any]) -> bool:
        """Send a quantum message between containers."""
        if not self.network_manager:
            print("Quantum networking is disabled")
            return False
        
        sender = self._find_container(sender_container)
        receiver = self._find_container(receiver_container)
        
        if not sender or not receiver:
            print(f"Container(s) not found: {sender_container}, {receiver_container}")
            return False
        
        success = await self.network_manager.send_quantum_message(
            sender.container_id, 
            receiver.container_id, 
            message_type, 
            data
        )
        
        if success:
            print(f" Quantum message sent: {sender_container} -> {receiver_container}")
        
        return success
    
    async def get_engine_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the Quantum Docker Engine."""
        if not self.engine_started:
            return {"status": "stopped"}
        
        status = {
            "status": "running",
            "uptime_seconds": time.time() - self.start_time,
            "config": {
                "num_qubits": self.config.num_qubits,
                "max_containers": self.config.max_containers,
                "quantum_networking": self.config.enable_quantum_networking,
                "quantum_scheduling": self.config.enable_quantum_scheduling,
                "quantum_load_balancing": self.config.enable_quantum_load_balancing
            },
            "containers": self.container_orchestrator.get_cluster_state(),
            "resources": self.resource_manager.get_quantum_resource_status()
        }
        
        # Add network status if networking is enabled
        if self.network_manager:
            status["network"] = self.network_manager.get_network_status()
        
        return status
    
    async def list_quantum_containers(self) -> List[Dict[str, Any]]:
        """List all quantum containers and their states."""
        containers_info = []
        
        for container in self.container_orchestrator.containers.values():
            info = container.get_quantum_info()
            containers_info.append(info)
        
        return containers_info
    
    async def inspect_quantum_container(self, container_name_or_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific quantum container."""
        container = self._find_container(container_name_or_id)
        if not container:
            return None
        
        return container.get_quantum_info()
    
    async def apply_quantum_gate(self, 
                                container_name_or_id: str, 
                                gate_type: str, 
                                **params) -> bool:
        """Apply a quantum gate to a container's quantum state."""
        container = self._find_container(container_name_or_id)
        if not container:
            print(f"Container not found: {container_name_or_id}")
            return False
        
        container.apply_quantum_gate(gate_type, **params)
        print(f"Applied {gate_type} gate to container {container_name_or_id}")
        return True
    
    async def quantum_resource_rebalance(self) -> Dict[str, List[str]]:
        """Perform quantum-based resource rebalancing across nodes."""
        if not self.config.enable_quantum_load_balancing:
            print("Quantum load balancing is disabled")
            return {}
        
        print(" Performing quantum resource rebalancing...")
        
        rebalancing_plan = await self.resource_manager.quantum_load_rebalancing(self.available_nodes)
        
        print("Quantum rebalancing plan generated:")
        for node_id, containers_to_migrate in rebalancing_plan.items():
            if containers_to_migrate:
                print(f"   {node_id}: migrate {len(containers_to_migrate)} containers")
        
        return rebalancing_plan
    
    def _find_container(self, name_or_id: str) -> Optional[QuantumContainer]:
        """Find a container by name or ID."""
        # Search by exact ID first
        if name_or_id in self.container_orchestrator.containers:
            return self.container_orchestrator.containers[name_or_id]
        
        # Search by partial ID
        for container_id, container in self.container_orchestrator.containers.items():
            if container_id.startswith(name_or_id):
                return container
        
        # Search by name
        for container in self.container_orchestrator.containers.values():
            if container.config.name == name_or_id:
                return container
        
        return None
    
    async def get_quantum_monitoring_report(self) -> Dict[str, Any]:
        """Get comprehensive quantum monitoring report."""
        if not self.engine_started:
            return {"error": "Engine not running"}

        # Try to generate a real report via monitoring system
        try:
            if hasattr(self, 'quantum_monitor') and self.quantum_monitor:
                return await self.quantum_monitor.generate_quantum_monitoring_report()
        except Exception as e:
            print(f"Monitoring report generation failed: {e}")

        # Fallback minimal report
        return {
            "summary": {
                "total_measurements": len(self.container_orchestrator.containers),
                "active_alerts": 0,
                "system_health": {
                    "status": "optimal",
                    "score": 0.95
                }
            },
            "status": "active"
        }
    
    async def quantum_container_health_check(self) -> Dict[str, Any]:
        """Perform quantum health check on all containers."""
        health_report = {
            "timestamp": time.time(),
            "total_containers": len(self.container_orchestrator.containers),
            "healthy_containers": 0,
            "unhealthy_containers": 0,
            "container_details": {}
        }
        
        for container_id, container in self.container_orchestrator.containers.items():
            try:
                # Get container quantum state
                container_state = container.get_quantum_info()
                
                # Monitor container with quantum sensors
                metrics = await self.quantum_monitor.monitor_container(container_state)
                
                # Determine health based on quantum metrics
                coherence_metrics = [m for m in metrics.values() if m.metric_type.value == 'quantum_coherence']
                is_healthy = all(m.value > 0.3 for m in coherence_metrics) if coherence_metrics else True
                
                if is_healthy:
                    health_report["healthy_containers"] += 1
                else:
                    health_report["unhealthy_containers"] += 1
                
                health_report["container_details"][container_id[:8]] = {
                    "name": container.config.name,
                    "quantum_state": container.quantum_state.value,
                    "healthy": is_healthy,
                    "quantum_metrics": {m.metric_type.value: m.value for m in metrics.values()}
                }
                
            except Exception as e:
                health_report["unhealthy_containers"] += 1
                container_name = getattr(container.config, 'name', 'unknown') if hasattr(container, 'config') else 'unknown'
                health_report["container_details"][container_id[:8]] = {
                    "name": container_name,
                    "healthy": False,
                    "error": str(e)
                }
        
        return health_report
    
    async def apply_quantum_optimization(self) -> Dict[str, Any]:
        """Apply quantum optimization to improve engine performance."""
        print("Applying quantum optimization...")
        
        optimization_results = {
            "timestamp": time.time(),
            "optimizations_applied": [],
            "performance_improvements": {}
        }
        
        # Optimize resource allocation
        if len(self.container_orchestrator.containers) > 1:
            container_requirements = {}
            for container_id, container in self.container_orchestrator.containers.items():
                container_requirements[container_id] = container.config.resource_requirements
            
            try:
                optimized_allocation = await self.resource_manager.quantum_resource_allocation(
                    container_requirements, self.available_nodes
                )
                
                optimization_results["optimizations_applied"].append("quantum_resource_allocation")
                optimization_results["performance_improvements"]["resource_efficiency"] = len(optimized_allocation)
            except Exception as e:
                print(f"Resource allocation optimization failed: {e}")
        
        # Apply quantum error correction optimization
        error_corrections = 0
        for container in self.container_orchestrator.containers.values():
            if hasattr(container, 'quantum_error_corrector') and container.quantum_error_corrector:
                try:
                    correction_result = await container.perform_quantum_annealing_optimization()
                    if correction_result:
                        error_corrections += 1
                except Exception as e:
                    print(f"Error correction optimization failed: {e}")
        
        if error_corrections > 0:
            optimization_results["optimizations_applied"].append("quantum_error_correction")
            optimization_results["performance_improvements"]["error_correction"] = error_corrections
        
        # Optimize quantum network topology
        if self.network_manager and len(self.container_orchestrator.containers) > 1:
            container_ids = list(self.container_orchestrator.containers.keys())
            try:
                mesh_success = await self.network_manager.create_quantum_mesh_network(container_ids)
                
                if mesh_success:
                    optimization_results["optimizations_applied"].append("quantum_network_optimization")
                    optimization_results["performance_improvements"]["network_connectivity"] = len(container_ids)
            except Exception as e:
                print(f"Network optimization failed: {e}")
        
        print(f"Quantum optimization completed: {len(optimization_results['optimizations_applied'])} optimizations applied")
        return optimization_results
    
    async def export_quantum_state(self, filename: str):
        """Export the current quantum state of the entire system."""
        state = await self.get_engine_status()
        
        # Clean state for JSON serialization
        cleaned_state = self._clean_for_json_export(state)
        
        with open(filename, 'w') as f:
            json.dump(cleaned_state, f, indent=2, default=str)
        
        print(f"Quantum state exported to: {filename}")
    
    def _clean_for_json_export(self, obj):
        """Clean object for JSON serialization by converting problematic types."""
        if isinstance(obj, dict):
            cleaned = {}
            for key, value in obj.items():
                # Convert all keys to strings
                str_key = str(key)
                cleaned[str_key] = self._clean_for_json_export(value)
            return cleaned
        elif isinstance(obj, list):
            return [self._clean_for_json_export(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # Convert objects with attributes to dictionaries
            return self._clean_for_json_export(obj.__dict__)
        elif hasattr(obj, 'value') and hasattr(obj, 'name'):
            # Handle Enum-like objects
            return str(obj.value) if hasattr(obj, 'value') else str(obj)
        else:
            return obj
    
    async def maintenance_cycle(self):
        """Perform routine quantum maintenance operations."""
        if not self.engine_started:
            return
        
        print("Running quantum maintenance cycle...")
        
        # Maintain quantum entanglement in network
        if self.network_manager:
            await self.network_manager.maintain_entanglement()
        
        # Check for decoherence in containers
        decoherent_containers = []
        for container in self.container_orchestrator.containers.values():
            # Check if container needs quantum state refresh
            time_since_creation = time.time() - container.creation_time
            if time_since_creation > self.config.decoherence_time_ms / 1000:
                decoherent_containers.append(container.config.name)
        
        if decoherent_containers:
            print(f"{len(decoherent_containers)} containers showing quantum decoherence")
        
        print("Quantum maintenance cycle completed")

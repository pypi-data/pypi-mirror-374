import click
import asyncio
import json
import yaml
import functools
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.engine import QuantumDockerEngine, QuantumEngineConfig
from ..core.quantum_resource_manager import ResourceType
from ..containers.quantum_container import QuantumContainer, QuantumContainerConfig, ContainerState
from .state_manager import state_manager

console = Console()


class QuantumDockerCLI:
    """Command Line Interface for Quantum Docker Engine."""
    
    def __init__(self):
        self.engine = None
        self.config_file = None
    
    async def load_engine(self, config_file=None):
        """Load the quantum docker engine with configuration."""
        # Check if engine is already running from previous session
        if state_manager.is_engine_running():
            existing_config = state_manager.get_engine_config()
            if existing_config:
                config = QuantumEngineConfig(**existing_config)
                self.engine = QuantumDockerEngine(config)
                # Restore engine state without restarting
                self.engine.engine_started = True
                self.engine.start_time = __import__('time').time()
                
                # Initialize quantum components
                await self.engine.resource_manager.initialize_quantum_resources(self.engine.available_nodes)
                
                # Restore containers from state
                saved_containers = state_manager.get_containers()
                if saved_containers:
                    # Restore containers in orchestrator
                    for container_data in saved_containers:
                        try:
                            # Create container config from saved data
                            config = QuantumContainerConfig(
                                image=container_data.get('image', 'restored:latest'),
                                name=container_data.get('name', 'unknown'),
                                quantum_weight=container_data.get('quantum_weight', 1.0),
                                quantum_probability=container_data.get('quantum_probability', 0.5),
                                superposition_states=container_data.get('superposition_states', ['running', 'stopped'])
                            )
                            
                            # Create and restore container
                            container = QuantumContainer(config, self.engine.circuit_manager)
                            container.container_id = container_data.get('container_id', container.container_id)
                            container.quantum_state = getattr(ContainerState, container_data.get('quantum_state', 'SUPERPOSITION').upper())
                            container.creation_time = container_data.get('creation_time', __import__('time').time())
                            # Restore classical/process id if present
                            container.classical_container_id = container_data.get('classical_container_id')
                            
                            # Restore superposition if needed
                            if container.quantum_state == ContainerState.SUPERPOSITION:
                                await container.create_superposition()
                            
                            # Add to orchestrator
                            self.engine.container_orchestrator.containers[container.container_id] = container
                            console.print(f"[dim green]Restored container: {container.config.name}[/dim green]")
                        except Exception as e:
                            console.print(f"[dim red]Failed to restore container {container_data.get('name', 'unknown')}: {e}[/dim red]")
                
                console.print("Connected to existing Quantum Docker Engine session")
                return
        
        if config_file:
            self.config_file = config_file
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                config = QuantumEngineConfig(
                    num_qubits=config_data.get('num_qubits', 16),
                    simulation_backend=config_data.get('simulation_backend', 'cirq'),
                    max_containers=config_data.get('max_containers', 50),
                    enable_quantum_networking=config_data.get('enable_quantum_networking', True),
                    enable_quantum_scheduling=config_data.get('enable_quantum_scheduling', True),
                    enable_quantum_load_balancing=config_data.get('enable_quantum_load_balancing', True),
                    decoherence_time_ms=config_data.get('decoherence_time_ms', 1000.0)
                )
                self.engine = QuantumDockerEngine(config)
                console.print(f"Loaded configuration from {config_file}")
            except Exception as e:
                console.print(f"Failed to load config: {e}")
                self.engine = QuantumDockerEngine()
        else:
            self.engine = QuantumDockerEngine()
    
    def format_quantum_info(self, container_info: Dict[str, Any]) -> Table:
        """Format quantum container information as a table."""
        table = Table(title=f"Quantum Container: {container_info['name']}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Container ID", container_info['container_id'][:8])
        table.add_row("Quantum State", container_info['quantum_state'])
        table.add_row("Creation Time", str(container_info['creation_time']))
        
        if container_info['state_amplitudes']:
            amplitudes_str = ", ".join([
                f"{state}: {amp[0]:.3f}+{amp[1]:.3f}i" 
                for state, amp in container_info['state_amplitudes'].items()
            ])
            table.add_row("State Amplitudes", amplitudes_str)
        
        if container_info['entangled_partners']:
            partners_str = ", ".join(container_info['entangled_partners'])
            table.add_row("Entangled Partners", partners_str)
        
        if container_info['classical_container_id']:
            table.add_row("Classical Container", container_info['classical_container_id'])
        
        return table


# Global CLI instance to maintain state across commands
cli = QuantumDockerCLI()

# Shared engine reference to prevent loss of containers
_shared_engine_ref = None

def get_shared_engine():
    global _shared_engine_ref
    if cli.engine and cli.engine.engine_started:
        _shared_engine_ref = cli.engine
    return _shared_engine_ref or cli.engine


@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.pass_context
def main(ctx, config):
    """Quantum Docker Engine - Container orchestration using quantum computing principles."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    
    # Show quantum docker banner
    banner = Text("QUANTUM DOCKER ENGINE", style="bold magenta")
    console.print(Panel(banner, expand=False))


@main.command()
@click.pass_context
def start(ctx):
    """Start the Quantum Docker Engine."""
    async def _start():
        await cli.load_engine(ctx.obj.get('config'))
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Starting Quantum Docker Engine...", total=None)
            await cli.engine.start_engine()
            progress.remove_task(task)
        
        # Save engine state for persistence
        config_dict = cli.engine.config.__dict__ if cli.engine.config else {}
        state_manager.save_engine_state(True, config_dict)
    
    asyncio.run(_start())


@main.command()
def stop():
    """Stop the Quantum Docker Engine."""
    async def _stop():
        # Load existing engine if needed
        if not cli.engine and state_manager.is_engine_running():
            await cli.load_engine()
        
        if not cli.engine or not cli.engine.engine_started:
            console.print("Quantum Docker Engine is not running")
            state_manager.clear_state()  # Clear stale state
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Stopping Quantum Docker Engine...", total=None)
            await cli.engine.stop_engine()
            progress.remove_task(task)
        
        # Clear persistent state
        state_manager.clear_state()
    
    asyncio.run(_stop())


@main.command()
def reset():
    """Reset local state: clears persisted engine state and locks."""
    # Stop engine if needed
    async def _reset():
        if cli.engine and cli.engine.engine_started:
            try:
                await cli.engine.stop_engine()
            except Exception:
                pass
        # Clear persistent state
        state_manager.clear_state()
        console.print("[green]Quantum Docker local state cleared[/green]")

    asyncio.run(_reset())


@main.command()
@click.argument('image')
@click.argument('name')
@click.option('--quantum-weight', default=1.0, help='Quantum weight for superposition')
@click.option('--quantum-probability', default=0.5, help='Quantum probability for measurement')
@click.option('--states', default='running,stopped', help='Comma-separated superposition states')
@click.option('--cpu', default=1.0, help='CPU requirement')
@click.option('--memory', default=512, help='Memory requirement in MB')
def create(image, name, quantum_weight, quantum_probability, states, cpu, memory):
    """Create a quantum container."""
    async def _create():
        # Load existing engine if needed
        if not cli.engine and state_manager.is_engine_running():
            await cli.load_engine()
        
        if not cli.engine or not cli.engine.engine_started:
            console.print("Quantum Docker Engine is not running. Use 'qdocker start' first.")
            return
        
        superposition_states = [s.strip() for s in states.split(',')]
        resource_requirements = {
            ResourceType.CPU: cpu,
            ResourceType.MEMORY: memory / 1024  # Convert MB to GB
        }
        
        try:
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task(f"Creating quantum container {name}...", total=None)
                
                container = await cli.engine.create_quantum_container(
                    image=image,
                    name=name,
                    quantum_weight=quantum_weight,
                    quantum_probability=quantum_probability,
                    superposition_states=superposition_states,
                    resource_requirements=resource_requirements
                )
                
                progress.remove_task(task)
            
            # Save updated container list to state (and ensure engine state exists)
            containers = await cli.engine.list_quantum_containers()
            console.print(f"[dim blue]Saving {len(containers)} containers to state[/dim blue]")
            state_manager.save_container_state(containers)
            # Ensure state file exists even if it was missing before
            try:
                state = state_manager.load_engine_state()
                if not state:
                    config_dict = cli.engine.config.__dict__ if cli.engine.config else {}
                    state_manager.save_engine_state(True, config_dict, containers)
            except Exception:
                pass
            
            container_info = container.get_quantum_info()
            console.print(cli.format_quantum_info(container_info))
            
        except Exception as e:
            console.print(f"Failed to create container: {e}")
    
    asyncio.run(_create())


@main.command()
@click.argument('container')
async def run(container):
    """Run a quantum container (performs measurement)."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"Running quantum container {container}...", total=None)
        success = await cli.engine.run_quantum_container(container)
        progress.remove_task(task)
    
    if success:
        console.print(f"Quantum container {container} is now running")
        # Persist updated container state (so classical/process id is restored later)
        try:
            containers = await cli.engine.list_quantum_containers()
            state_manager.save_container_state(containers)
        except Exception:
            pass
    else:
        console.print(f"Failed to run quantum container {container}")


@main.command()
@click.argument('container')
async def stop_container(container):
    """Stop a quantum container."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    success = await cli.engine.stop_quantum_container(container)
    if success:
        console.print(f"Quantum container {container} stopped")


@main.command()
@click.argument('container')
async def measure(container):
    """Perform quantum measurement on a container."""
    # Load existing engine if needed
    if not cli.engine and state_manager.is_engine_running():
        await cli.load_engine()
        
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"Measuring quantum state of {container}...", total=None)
        measured_state = await cli.engine.measure_container(container)
        progress.remove_task(task)
    
    if measured_state:
        console.print(f"Container {container} measured in state: [bold cyan]{measured_state}[/bold cyan]")
    else:
        console.print(f"Failed to measure container {container}")


@main.command()
@click.argument('container1')
@click.argument('container2')
async def entangle(container1, container2):
    """Create quantum entanglement between two containers."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task(f"Entangling {container1} and {container2}...", total=None)
        success = await cli.engine.entangle_containers(container1, container2)
        progress.remove_task(task)
    
    if success:
        console.print(f"Containers {container1} and {container2} are now entangled")


@main.command()
def ps():
    """List quantum containers."""
    async def _ps():
        # Load existing engine if marked running in state
        if not cli.engine and state_manager.is_engine_running():
            await cli.load_engine()

        engine_running = bool(cli.engine and cli.engine.engine_started)

        # Try live engine first
        containers = []
        if engine_running:
            try:
                containers = await cli.engine.list_quantum_containers()
            except Exception:
                containers = []

        # Fallback to persisted state when live engine has none or isn't running
        if not containers:
            persisted = state_manager.get_containers()
            if persisted:
                if not engine_running:
                    console.print("[dim yellow]Engine not running; showing last saved containers[/dim yellow]")
                containers = persisted
            else:
                if not engine_running:
                    console.print("Quantum Docker Engine is not running and no saved containers found")
                else:
                    console.print("No quantum containers found")
                return
        
        table = Table(title="Quantum Containers")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Quantum State", style="green")
        table.add_column("Entangled", style="yellow")
        table.add_column("Classical ID", style="blue")
        
        for container in containers:
            table.add_row(
                container['container_id'][:8],
                container['name'],
                container['quantum_state'],
                str(len(container['entangled_partners'])),
                container['classical_container_id'] or "N/A"
            )
        
        console.print(table)
    
    asyncio.run(_ps())


@main.command()
@click.argument('container')
async def inspect(container):
    """Inspect a quantum container."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    container_info = await cli.engine.inspect_quantum_container(container)
    if container_info:
        console.print(cli.format_quantum_info(container_info))
    else:
        console.print(f"Container not found: {container}")


@main.command()
@click.argument('cluster_config_file')
async def create_cluster(cluster_config_file):
    """Create a quantum cluster from configuration file."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    try:
        with open(cluster_config_file, 'r') as f:
            cluster_config = yaml.safe_load(f)
        
        cluster_name = cluster_config.get('name', 'quantum-cluster')
        container_configs = cluster_config.get('containers', [])
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task(f"Creating quantum cluster {cluster_name}...", total=None)
            
            containers = await cli.engine.create_quantum_cluster(container_configs, cluster_name)
            progress.remove_task(task)
        
        console.print(f"Created quantum cluster '{cluster_name}' with {len(containers)} containers")
        
        # Show cluster information
        table = Table(title=f"Quantum Cluster: {cluster_name}")
        table.add_column("Container", style="cyan")
        table.add_column("Image", style="white")
        table.add_column("Quantum State", style="green")
        
        for container in containers:
            table.add_row(
                container.config.name,
                container.config.image,
                container.quantum_state.value
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"Failed to create cluster: {e}")


@main.command()
@click.argument('containers', nargs=-1)
async def load_balance(containers):
    """Perform quantum load balancing on containers."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    if not containers:
        console.print("Please specify containers to load balance")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Performing quantum load balancing...", total=None)
        allocation = await cli.engine.quantum_load_balance(list(containers))
        progress.remove_task(task)
    
    if allocation:
        table = Table(title="Quantum Load Balancing Results")
        table.add_column("Container", style="cyan")
        table.add_column("Assigned Node", style="green")
        
        for container, node in allocation.items():
            table.add_row(container, node)
        
        console.print(table)


@main.command()
@click.argument('sender')
@click.argument('receiver')
@click.argument('message_type')
@click.option('--data', default='{}', help='JSON data to send')
async def send_message(sender, receiver, message_type, data):
    """Send a quantum message between containers."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    try:
        message_data = json.loads(data)
        success = await cli.engine.send_quantum_message(sender, receiver, message_type, message_data)
        
        if success:
            console.print(f" Quantum message sent: {sender} -> {receiver}")
        else:
            console.print(f"Failed to send quantum message")
    except json.JSONDecodeError:
        console.print(f"Invalid JSON data: {data}")


@main.command()
@click.argument('container')
@click.argument('gate_type')
@click.option('--angle', type=float, help='Rotation angle for parameterized gates')
async def apply_gate(container, gate_type, angle):
    """Apply a quantum gate to a container."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    params = {}
    if angle is not None:
        params['angle'] = angle
    
    success = await cli.engine.apply_quantum_gate(container, gate_type, **params)
    if not success:
        console.print(f"Failed to apply {gate_type} gate to {container}")


@main.command()
def status():
    """Show Quantum Docker Engine status."""
    async def _status():
        # Load existing engine if needed
        if not cli.engine and state_manager.is_engine_running():
            await cli.load_engine()
        
        if not cli.engine:
            console.print("Quantum Docker Engine is not initialized")
            return
        
        status = await cli.engine.get_engine_status()
        
        if status['status'] == 'stopped':
            console.print("Quantum Docker Engine is stopped")
            return
        
        # Engine information
        engine_table = Table(title="Quantum Docker Engine Status")
        engine_table.add_column("Property", style="cyan")
        engine_table.add_column("Value", style="white")
        
        engine_table.add_row("Status", f"{status['status']}")
        engine_table.add_row("Uptime", f"{status['uptime_seconds']:.1f} seconds")
        engine_table.add_row("Qubits", str(status['config']['num_qubits']))
        engine_table.add_row("Max Containers", str(status['config']['max_containers']))
        engine_table.add_row("Quantum Networking", "Enabled" if status['config']['quantum_networking'] else "Disabled")
        engine_table.add_row("Quantum Scheduling", "Enabled" if status['config']['quantum_scheduling'] else "Disabled")
        
        console.print(engine_table)
        
        # Container information
        containers_info = status['containers']
        console.print(f"\nTotal Containers: {containers_info['total_containers']}")
        
        # Resource information
        resources_info = status['resources']
        console.print(f"System Quantum Coherence: {resources_info['quantum_coherence']:.3f}")
        
        # Network information
        if 'network' in status:
            network_info = status['network']
            console.print(f" Quantum Channels: {network_info['active_channels']}/{network_info['total_channels']}")
    
    asyncio.run(_status())


@main.command()
async def rebalance():
    """Perform quantum resource rebalancing."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Performing quantum resource rebalancing...", total=None)
        rebalancing_plan = await cli.engine.quantum_resource_rebalance()
        progress.remove_task(task)
    
    if any(rebalancing_plan.values()):
        table = Table(title="Quantum Rebalancing Plan")
        table.add_column("Node", style="cyan")
        table.add_column("Containers to Migrate", style="yellow")
        
        for node, containers in rebalancing_plan.items():
            if containers:
                table.add_row(node, ", ".join([c[:8] for c in containers]))
        
        console.print(table)
    else:
        console.print("No rebalancing needed - system is optimally balanced")


@main.command()
@click.option('--filename', default='quantum_state.json', help='Output filename')
async def export_state(filename):
    """Export quantum state to file."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    await cli.engine.export_quantum_state(filename)


@main.command()
async def maintenance():
    """Run quantum maintenance cycle."""
    if not cli.engine or not cli.engine.engine_started:
        console.print("Quantum Docker Engine is not running")
        return
    
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        task = progress.add_task("Running quantum maintenance...", total=None)
        await cli.engine.maintenance_cycle()
        progress.remove_task(task)


# Convert async commands to sync for Click
def async_command(f):
    """Decorator to convert async commands to sync for Click."""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

# Apply async decorator to all async commands
for name, command in list(main.commands.items()):
    # Get the actual function (might be wrapped by click decorators)
    actual_func = command.callback
    # Check if it's a coroutine function
    if asyncio.iscoroutinefunction(actual_func):
        command.callback = async_command(actual_func)


if __name__ == '__main__':
    main()

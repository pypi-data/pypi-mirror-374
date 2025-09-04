#!/usr/bin/env python3
"""
Quantum Docker Engine State Manager
Handles persistent state between CLI commands
"""

import os
import json
import pickle
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio


class QuantumStateManager:
    """Manages persistent state for Quantum Docker CLI commands."""
    
    def __init__(self):
        self.state_dir = Path.home() / ".quantum_docker"
        self.state_file = self.state_dir / "engine_state.json"
        self.pid_file = self.state_dir / "engine.pid"
        self.socket_file = self.state_dir / "engine.sock"
        
        # Ensure state directory exists
        self.state_dir.mkdir(exist_ok=True)
    
    def save_engine_state(self, engine_started: bool, config: Dict[str, Any], containers: list = None):
        """Save current engine state to persistent storage."""
        state_data = {
            "engine_started": engine_started,
            "config": config,
            "containers": containers or [],
            "timestamp": __import__('time').time() if engine_started else 0,
            "pid": os.getpid() if engine_started else None
        }
        
        try:
            # Write to temporary file first, then rename for atomic operation
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            temp_file.replace(self.state_file)
            pass
        except Exception as e:
            pass
            pass  # Fail silently to not break CLI
    
    def load_engine_state(self) -> Optional[Dict[str, Any]]:
        """Load engine state from persistent storage."""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def is_engine_running(self) -> bool:
        """Check if engine is currently running."""
        state = self.load_engine_state()
        if not state:
            return False
        
        return state.get("engine_started", False)
    
    def get_engine_config(self) -> Optional[Dict[str, Any]]:
        """Get the last used engine configuration."""
        state = self.load_engine_state()
        if not state:
            return None
        
        return state.get("config")
    
    def get_containers(self) -> list:
        """Get list of containers from last session."""
        state = self.load_engine_state()
        if not state:
            return []
        
        return state.get("containers", [])
    
    def clear_state(self):
        """Clear persistent state (when engine is stopped)."""
        try:
            if self.state_file.exists():
                self.state_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception:
            pass
    
    def save_container_state(self, containers: list):
        """Update container list in persistent state."""
        state = self.load_engine_state()
        # Clean containers data for JSON serialization
        clean_containers = []
        for container in containers:
            if isinstance(container, dict):
                # Convert complex numbers to simple values
                clean_container = container.copy()
                if 'state_amplitudes' in clean_container:
                    amplitudes = {}
                    for k, v in clean_container['state_amplitudes'].items():
                        if isinstance(v, list) and len(v) == 2:
                            amplitudes[k] = f"{v[0]:.3f}+{v[1]:.3f}i"
                        else:
                            amplitudes[k] = str(v)
                    clean_container['state_amplitudes'] = amplitudes
                clean_containers.append(clean_container)
            else:
                clean_containers.append(str(container))

        # If no state exists yet, create a minimal one so `ps` can read persisted containers
        if not state:
            self.save_engine_state(
                True,  # assume engine is running if we're saving containers
                {},
                clean_containers
            )
            return

        # Update existing state
        state["containers"] = clean_containers
        self.save_engine_state(
            state.get("engine_started", True),
            state.get("config", {}),
            clean_containers
        )


# Global state manager instance
state_manager = QuantumStateManager()

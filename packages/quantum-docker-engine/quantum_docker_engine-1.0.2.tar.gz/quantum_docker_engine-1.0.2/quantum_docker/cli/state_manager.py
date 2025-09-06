#!/usr/bin/env python3
"""
Quantum Docker Engine State Manager
Handles persistent state between CLI commands
"""

import os
import json
import fcntl
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio


class QuantumStateManager:
    """Manages persistent state for Quantum Docker CLI commands."""
    
    def __init__(self):
        self.state_dir = Path.home() / ".quantum_docker"
        self.state_file = self.state_dir / "engine_state.json"
        self.lock_file = self.state_dir / "engine.lock"
        self.pid_file = self.state_dir / "engine.pid"
        self.socket_file = self.state_dir / "engine.sock"
        
        # Ensure state directory exists
        self.state_dir.mkdir(exist_ok=True)

    @contextmanager
    def _lock(self):
        with open(self.lock_file, 'w') as fp:
            fcntl.flock(fp, fcntl.LOCK_EX)
            yield
            fcntl.flock(fp, fcntl.LOCK_UN)

    def save_engine_state(self, engine_started: bool, config: Dict[str, Any], containers: list = None):
        """Save current engine state to persistent storage."""
        with self._lock():
            existing_state = self._load_engine_state_unlocked() or {}

            if containers is None:
                containers = existing_state.get('containers', [])

            self._save_engine_state_unlocked(engine_started, config, containers)

    def _save_engine_state_unlocked(self, engine_started: bool, config: Dict[str, Any], containers: list):
        """Write engine state without acquiring the lock (caller must hold it)."""
        state_data = {
            "engine_started": engine_started,
            "config": config,
            "containers": containers,
            "timestamp": __import__('time').time() if engine_started else 0,
            "pid": os.getpid() if engine_started else None
        }

        temp_file = self.state_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(state_data, f, indent=2, default=str)
        temp_file.replace(self.state_file)
    
    def _load_engine_state_unlocked(self) -> Optional[Dict[str, Any]]:
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None

    def load_engine_state(self) -> Optional[Dict[str, Any]]:
        """Load engine state from persistent storage."""
        with self._lock():
            return self._load_engine_state_unlocked()
    
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
        # Remove tracked files under lock, then drop the lock file itself
        with self._lock():
            if self.state_file.exists():
                self.state_file.unlink()
            if self.pid_file.exists():
                self.pid_file.unlink()
            if self.socket_file.exists():
                try:
                    self.socket_file.unlink()
                except Exception:
                    pass
        # Remove lock file after releasing the lock
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
        except Exception:
            pass
    
    def save_container_state(self, containers: list):
        """Update container list in persistent state.
        Persist only lightweight, restore-relevant fields to keep writes fast.
        """
        with self._lock():
            state = self._load_engine_state_unlocked() or {}

            # Keep minimal fields for fast persistence and restore
            allowed_keys = {
                'container_id', 'name', 'image',
                'quantum_weight', 'quantum_probability',
                'superposition_states', 'quantum_state',
                'entangled_partners', 'creation_time',
                'classical_container_id'
            }

            clean_containers = []
            for container in containers:
                if isinstance(container, dict):
                    minimal = {k: container.get(k) for k in allowed_keys}

                    # Defaults and type normalization
                    if minimal.get('classical_container_id', None) is None:
                        minimal['classical_container_id'] = None
                    try:
                        minimal['creation_time'] = float(minimal.get('creation_time', 0))
                    except Exception:
                        minimal['creation_time'] = 0.0
                    if not isinstance(minimal.get('superposition_states'), list):
                        val = minimal.get('superposition_states')
                        minimal['superposition_states'] = list(val) if val is not None else []
                    if not isinstance(minimal.get('entangled_partners'), list):
                        val = minimal.get('entangled_partners')
                        minimal['entangled_partners'] = list(val) if val is not None else []

                    clean_containers.append(minimal)
                else:
                    clean_containers.append(str(container))

            state['containers'] = clean_containers
            self._save_engine_state_unlocked(
                state.get('engine_started', True),
                state.get('config', {}),
                clean_containers
            )


# Global state manager instance
state_manager = QuantumStateManager()

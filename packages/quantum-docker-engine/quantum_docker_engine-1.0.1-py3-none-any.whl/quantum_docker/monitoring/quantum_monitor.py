"""
Quantum Container Monitoring System
Advanced quantum-based monitoring using quantum sensors, entanglement detection,
and quantum state analysis for comprehensive container observability.
"""

import cirq
import numpy as np
import asyncio
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt
from collections import deque


class QuantumMetricType(Enum):
    """Types of quantum metrics for monitoring."""
    QUANTUM_COHERENCE = "quantum_coherence"
    ENTANGLEMENT_STRENGTH = "entanglement_strength"
    DECOHERENCE_RATE = "decoherence_rate"
    QUANTUM_FIDELITY = "quantum_fidelity"
    SUPERPOSITION_PURITY = "superposition_purity"
    QUANTUM_INTERFERENCE = "quantum_interference"
    ERROR_RATE = "quantum_error_rate"
    TUNNELING_EVENTS = "quantum_tunneling_events"


@dataclass
class QuantumMetric:
    """Represents a quantum metric measurement."""
    metric_type: QuantumMetricType
    value: float
    timestamp: float
    container_id: str
    node_id: str
    confidence: float = 0.9
    quantum_uncertainty: float = 0.05


@dataclass
class QuantumAlert:
    """Quantum-based alert for monitoring."""
    alert_id: str
    severity: str  # "info", "warning", "critical"
    message: str
    metric_type: QuantumMetricType
    threshold_value: float
    actual_value: float
    container_id: str
    timestamp: float
    quantum_probability: float = 0.9


class QuantumSensor:
    """Quantum sensor for measuring container states."""
    
    def __init__(self, sensor_id: str, metric_type: QuantumMetricType):
        self.sensor_id = sensor_id
        self.metric_type = metric_type
        self.qubits = cirq.LineQubit.range(3)  # 3 qubits per sensor
        self.simulator = cirq.Simulator()
        self.calibration_offset = np.random.uniform(-0.05, 0.05)
        self.measurement_history = deque(maxlen=1000)
        
    async def measure_quantum_state(self, container_quantum_state: Dict[str, Any]) -> QuantumMetric:
        """Perform quantum measurement using quantum sensor."""
        
        # Create quantum sensor circuit
        circuit = cirq.Circuit()
        
        # Initialize sensor qubits based on container state
        container_amplitudes = container_quantum_state.get('state_amplitudes', {})
        
        # Encode container state into sensor qubits
        for i, qubit in enumerate(self.qubits):
            if i < len(container_amplitudes):
                # Apply rotation based on container amplitude
                amplitude_values = list(container_amplitudes.values())
                if i < len(amplitude_values):
                    amplitude = amplitude_values[i]
                    if isinstance(amplitude, list) and len(amplitude) >= 2:
                        angle = np.arctan2(amplitude[1], amplitude[0])
                        circuit.append(cirq.ry(angle)(qubit))
            
            # Add measurement noise
            circuit.append(cirq.depolarize(0.01)(qubit))
        
        # Perform quantum measurement based on metric type
        if self.metric_type == QuantumMetricType.QUANTUM_COHERENCE:
            measurement_value = await self._measure_coherence(circuit)
        elif self.metric_type == QuantumMetricType.ENTANGLEMENT_STRENGTH:
            measurement_value = await self._measure_entanglement(circuit)
        elif self.metric_type == QuantumMetricType.DECOHERENCE_RATE:
            measurement_value = await self._measure_decoherence_rate(circuit)
        elif self.metric_type == QuantumMetricType.QUANTUM_FIDELITY:
            measurement_value = await self._measure_fidelity(circuit)
        else:
            measurement_value = await self._generic_measurement(circuit)
        
        # Apply calibration and noise
        measurement_value += self.calibration_offset
        measurement_value += np.random.normal(0, 0.02)  # Measurement noise
        measurement_value = np.clip(measurement_value, 0.0, 1.0)
        
        # Create metric
        metric = QuantumMetric(
            metric_type=self.metric_type,
            value=measurement_value,
            timestamp=time.time(),
            container_id=container_quantum_state.get('container_id', 'unknown'),
            node_id=container_quantum_state.get('node_id', 'unknown'),
            confidence=np.random.uniform(0.85, 0.99),
            quantum_uncertainty=np.random.uniform(0.01, 0.05)
        )
        
        self.measurement_history.append(metric)
        return metric
    
    async def _measure_coherence(self, circuit: cirq.Circuit) -> float:
        """Measure quantum coherence."""
        # Add coherence measurement operations
        coherence_circuit = circuit.copy()
        
        # Apply Hadamard and measure
        for qubit in self.qubits:
            coherence_circuit.append(cirq.H(qubit))
        
        coherence_circuit.append(cirq.measure(*self.qubits, key='coherence'))
        
        result = self.simulator.run(coherence_circuit, repetitions=100)
        measurements = result.measurements['coherence']
        
        # Calculate coherence from measurement statistics
        variance = np.var(measurements.astype(float))
        coherence = 1.0 / (1.0 + variance)  # Higher variance = lower coherence
        
        return coherence
    
    async def _measure_entanglement(self, circuit: cirq.Circuit) -> float:
        """Measure entanglement strength."""
        entanglement_circuit = circuit.copy()
        
        # Create Bell measurement
        if len(self.qubits) >= 2:
            entanglement_circuit.append(cirq.CNOT(self.qubits[0], self.qubits[1]))
            entanglement_circuit.append(cirq.H(self.qubits[0]))
        
        entanglement_circuit.append(cirq.measure(*self.qubits[:2], key='entanglement'))
        
        result = self.simulator.run(entanglement_circuit, repetitions=100)
        measurements = result.measurements['entanglement']
        
        # Calculate entanglement from Bell measurement
        correlations = []
        for measurement in measurements:
            if len(measurement) >= 2:
                correlation = 1 if measurement[0] == measurement[1] else -1
                correlations.append(correlation)
        
        entanglement_strength = abs(np.mean(correlations)) if correlations else 0.0
        return entanglement_strength
    
    async def _measure_decoherence_rate(self, circuit: cirq.Circuit) -> float:
        """Measure decoherence rate."""
        # Measure at different time intervals
        measurements = []
        
        for delay in [0, 10, 20, 30]:  # Different delays
            delayed_circuit = circuit.copy()
            
            # Add time evolution (simplified)
            for qubit in self.qubits:
                delayed_circuit.append(cirq.rz(delay * 0.01)(qubit))
            
            delayed_circuit.append(cirq.measure(*self.qubits, key=f'decohere_{delay}'))
            
            result = self.simulator.run(delayed_circuit, repetitions=50)
            measurement_variance = np.var(result.measurements[f'decohere_{delay}'].astype(float))
            measurements.append(measurement_variance)
        
        # Calculate decoherence rate from variance increase
        if len(measurements) > 1:
            decoherence_rate = (measurements[-1] - measurements[0]) / len(measurements)
            return min(abs(decoherence_rate), 1.0)
        
        return 0.1  # Default value
    
    async def _measure_fidelity(self, circuit: cirq.Circuit) -> float:
        """Measure quantum fidelity."""
        fidelity_circuit = circuit.copy()
        
        # Add fidelity measurement operations
        for qubit in self.qubits:
            # Random unitary for fidelity test
            angle = np.random.uniform(0, 2*np.pi)
            fidelity_circuit.append(cirq.rz(angle)(qubit))
        
        fidelity_circuit.append(cirq.measure(*self.qubits, key='fidelity'))
        
        result = self.simulator.run(fidelity_circuit, repetitions=100)
        measurements = result.measurements['fidelity']
        
        # Calculate fidelity from measurement consistency
        expected_pattern = measurements[0] if len(measurements) > 0 else []
        matches = sum(1 for m in measurements if np.array_equal(m, expected_pattern))
        fidelity = matches / len(measurements) if len(measurements) > 0 else 0.0
        
        return fidelity
    
    async def _generic_measurement(self, circuit: cirq.Circuit) -> float:
        """Generic quantum measurement."""
        measurement_circuit = circuit.copy()
        measurement_circuit.append(cirq.measure(*self.qubits, key='generic'))
        
        result = self.simulator.run(measurement_circuit, repetitions=100)
        measurements = result.measurements['generic']
        
        # Return normalized average
        return np.mean(measurements.astype(float)) / len(self.qubits)


class QuantumMonitoringSystem:
    """Advanced quantum monitoring system for containers."""
    
    def __init__(self, num_sensors: int = 8):
        self.sensors: Dict[str, QuantumSensor] = {}
        self.metrics_history: Dict[str, deque] = {}
        self.alerts: List[QuantumAlert] = []
        self.monitoring_active = False
        self.alert_thresholds = self._initialize_thresholds()
        
        # Initialize quantum sensors
        self._initialize_sensors(num_sensors)
        
    def _initialize_sensors(self, num_sensors: int):
        """Initialize quantum sensors for different metrics."""
        metric_types = list(QuantumMetricType)
        
        for i in range(num_sensors):
            metric_type = metric_types[i % len(metric_types)]
            sensor_id = f"qsensor_{i}_{metric_type.value}"
            self.sensors[sensor_id] = QuantumSensor(sensor_id, metric_type)
            self.metrics_history[sensor_id] = deque(maxlen=10000)
    
    def _initialize_thresholds(self) -> Dict[QuantumMetricType, Dict[str, float]]:
        """Initialize alert thresholds for quantum metrics."""
        return {
            QuantumMetricType.QUANTUM_COHERENCE: {
                "warning": 0.3,
                "critical": 0.1
            },
            QuantumMetricType.ENTANGLEMENT_STRENGTH: {
                "warning": 0.5,
                "critical": 0.2
            },
            QuantumMetricType.DECOHERENCE_RATE: {
                "warning": 0.7,
                "critical": 0.9
            },
            QuantumMetricType.QUANTUM_FIDELITY: {
                "warning": 0.4,
                "critical": 0.2
            },
            QuantumMetricType.SUPERPOSITION_PURITY: {
                "warning": 0.3,
                "critical": 0.1
            },
            QuantumMetricType.ERROR_RATE: {
                "warning": 0.1,
                "critical": 0.3
            }
        }
    
    async def start_monitoring(self):
        """Start quantum monitoring system."""
        self.monitoring_active = True
        print(" Quantum monitoring system started")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop_monitoring(self):
        """Stop quantum monitoring system."""
        self.monitoring_active = False
        print(" Quantum monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # This would be called with actual container states
                # For now, simulate monitoring
                await self._simulate_monitoring_cycle()
                await asyncio.sleep(1.0)  # 1 second monitoring interval
                
            except Exception as e:
                print(f"Monitoring loop error: {e}")
                await asyncio.sleep(5.0)
    
    async def _simulate_monitoring_cycle(self):
        """Simulate a monitoring cycle (for demonstration)."""
        # In real implementation, this would get container states from orchestrator
        simulated_container_state = {
            'container_id': f'sim_container_{int(time.time()) % 1000}',
            'node_id': 'localhost',
            'state_amplitudes': {
                'running': [0.8, 0.1],
                'stopped': [0.2, -0.05],
                'suspended': [0.0, 0.0]
            }
        }
        
        await self.monitor_container(simulated_container_state)
    
    async def monitor_container(self, container_state: Dict[str, Any]) -> Dict[str, QuantumMetric]:
        """Monitor a specific container using quantum sensors."""
        metrics = {}
        
        for sensor_id, sensor in self.sensors.items():
            try:
                metric = await sensor.measure_quantum_state(container_state)
                metrics[sensor_id] = metric
                
                # Store in history
                self.metrics_history[sensor_id].append(metric)
                
                # Check for alerts
                await self._check_alerts(metric)
                
            except Exception as e:
                print(f"Sensor {sensor_id} measurement failed: {e}")
        
        return metrics
    
    async def _check_alerts(self, metric: QuantumMetric):
        """Check if metric triggers any alerts."""
        thresholds = self.alert_thresholds.get(metric.metric_type)
        if not thresholds:
            return
        
        severity = None
        if metric.value <= thresholds.get("critical", 0):
            severity = "critical"
        elif metric.value <= thresholds.get("warning", 0):
            severity = "warning"
        
        if severity:
            alert = QuantumAlert(
                alert_id=f"alert_{metric.container_id}_{int(time.time())}",
                severity=severity,
                message=f"{metric.metric_type.value} is {severity}: {metric.value:.3f}",
                metric_type=metric.metric_type,
                threshold_value=thresholds[severity],
                actual_value=metric.value,
                container_id=metric.container_id,
                timestamp=time.time(),
                quantum_probability=metric.confidence
            )
            
            self.alerts.append(alert)
            print(f" Quantum Alert [{severity.upper()}]: {alert.message}")
    
    def get_quantum_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of quantum monitoring metrics."""
        summary = {
            'total_sensors': len(self.sensors),
            'total_measurements': sum(len(history) for history in self.metrics_history.values()),
            'active_alerts': len([a for a in self.alerts if time.time() - a.timestamp < 300]),  # Last 5 minutes
            'recent_metrics': {},
            'system_health': self._calculate_system_health()
        }
        
        # Get recent metrics for each type
        for metric_type in QuantumMetricType:
            recent_values = []
            for sensor_id, sensor in self.sensors.items():
                if sensor.metric_type == metric_type and self.metrics_history[sensor_id]:
                    recent_metric = self.metrics_history[sensor_id][-1]
                    recent_values.append(recent_metric.value)
            
            if recent_values:
                summary['recent_metrics'][metric_type.value] = {
                    'average': np.mean(recent_values),
                    'min': np.min(recent_values),
                    'max': np.max(recent_values),
                    'std': np.std(recent_values)
                }
        
        return summary
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall quantum system health."""
        if not self.metrics_history:
            return {'status': 'unknown', 'score': 0.0}
        
        health_scores = []
        
        # Calculate health based on recent metrics
        for sensor_id, history in self.metrics_history.items():
            if history:
                recent_metric = history[-1]
                sensor = self.sensors[sensor_id]
                
                # Health score based on thresholds
                thresholds = self.alert_thresholds.get(sensor.metric_type, {})
                warning_threshold = thresholds.get('warning', 0.5)
                critical_threshold = thresholds.get('critical', 0.2)
                
                if recent_metric.value >= warning_threshold:
                    health_scores.append(1.0)  # Healthy
                elif recent_metric.value >= critical_threshold:
                    health_scores.append(0.5)  # Warning
                else:
                    health_scores.append(0.0)  # Critical
        
        overall_health = np.mean(health_scores) if health_scores else 0.0
        
        if overall_health >= 0.8:
            status = 'healthy'
        elif overall_health >= 0.5:
            status = 'warning'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'score': overall_health,
            'total_sensors': len(health_scores)
        }
    
    async def generate_quantum_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive quantum monitoring report."""
        report = {
            'timestamp': time.time(),
            'monitoring_duration': time.time() - (self.metrics_history[list(self.metrics_history.keys())[0]][0].timestamp if self.metrics_history and list(self.metrics_history.values())[0] else time.time()),
            'summary': self.get_quantum_metrics_summary(),
            'alerts': {
                'total': len(self.alerts),
                'critical': len([a for a in self.alerts if a.severity == 'critical']),
                'warning': len([a for a in self.alerts if a.severity == 'warning']),
                'recent': [
                    {
                        'severity': alert.severity,
                        'message': alert.message,
                        'container_id': alert.container_id,
                        'timestamp': alert.timestamp
                    } for alert in self.alerts[-10:]  # Last 10 alerts
                ]
            },
            'sensor_status': {},
            'quantum_insights': await self._generate_quantum_insights()
        }
        
        # Add sensor status
        for sensor_id, sensor in self.sensors.items():
            history = self.metrics_history[sensor_id]
            report['sensor_status'][sensor_id] = {
                'metric_type': sensor.metric_type.value,
                'total_measurements': len(history),
                'last_measurement': history[-1].value if history else None,
                'average_value': np.mean([m.value for m in history]) if history else 0.0,
                'calibration_offset': sensor.calibration_offset
            }
        
        return report
    
    async def _generate_quantum_insights(self) -> Dict[str, Any]:
        """Generate quantum insights from monitoring data."""
        insights = {
            'coherence_trends': 'stable',
            'entanglement_quality': 'good',
            'decoherence_patterns': 'normal',
            'recommendations': []
        }
        
        # Analyze coherence trends
        coherence_sensors = [s for s in self.sensors.values() if s.metric_type == QuantumMetricType.QUANTUM_COHERENCE]
        if coherence_sensors:
            coherence_values = []
            for sensor in coherence_sensors:
                history = self.metrics_history[sensor.sensor_id]
                if len(history) >= 2:
                    recent_values = [m.value for m in history[-10:]]
                    coherence_values.extend(recent_values)
            
            if coherence_values:
                if np.mean(coherence_values) < 0.3:
                    insights['coherence_trends'] = 'declining'
                    insights['recommendations'].append('Consider quantum error correction enhancement')
                elif np.std(coherence_values) > 0.2:
                    insights['coherence_trends'] = 'unstable'
                    insights['recommendations'].append('Investigate coherence fluctuations')
        
        # Analyze entanglement quality
        entanglement_sensors = [s for s in self.sensors.values() if s.metric_type == QuantumMetricType.ENTANGLEMENT_STRENGTH]
        if entanglement_sensors:
            entanglement_values = []
            for sensor in entanglement_sensors:
                history = self.metrics_history[sensor.sensor_id]
                recent_values = [m.value for m in history[-5:]]
                entanglement_values.extend(recent_values)
            
            if entanglement_values and np.mean(entanglement_values) < 0.4:
                insights['entanglement_quality'] = 'poor'
                insights['recommendations'].append('Re-establish quantum entanglement channels')
        
        return insights
    
    def export_monitoring_data(self, filename: str = None) -> str:
        """Export monitoring data to JSON file."""
        if filename is None:
            filename = f"quantum_monitoring_{int(time.time())}.json"
        
        export_data = {
            'sensors': {
                sensor_id: {
                    'metric_type': sensor.metric_type.value,
                    'measurements': [
                        {
                            'value': m.value,
                            'timestamp': m.timestamp,
                            'confidence': m.confidence,
                            'uncertainty': m.quantum_uncertainty
                        } for m in self.metrics_history[sensor_id]
                    ]
                } for sensor_id, sensor in self.sensors.items()
            },
            'alerts': [
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity,
                    'message': alert.message,
                    'metric_type': alert.metric_type.value,
                    'container_id': alert.container_id,
                    'timestamp': alert.timestamp
                } for alert in self.alerts
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f" Monitoring data exported to: {filename}")
        return filename
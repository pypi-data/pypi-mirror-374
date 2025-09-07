# AriQuantum: Python Library for Quantum Computing Simulation

AriQuantum is a powerful and intuitive Python library for quantum computing simulation, designed for education, research, and experimentation in quantum technologies.

## 🌟 Key Features

- **Complete qubit and multi-qubit system simulation**
- **Rich set of quantum gates**: Pauli, Hadamard, phase, controlled operations, and more
- **Circuit visualization** in text and graphical formats
- **Bloch sphere representation** of quantum states
- **Flexible measurements** with support for deferred measurement
- **Statistical analysis** of measurement results

## 🚀 Quick Start

### Installation

```bash
pip install ariquantum
```

### Basic Examples

#### Working with Single Qubits

```python
from src.ariquantum import Qubit

# Creating qubits in various states
q0 = Qubit('0')  # Basis state |0⟩
q1 = Qubit('1')  # Basis state |1⟩ 
q_plus = Qubit('+')  # Superposition (|0⟩ + |1⟩)/√2
q_minus = Qubit('-')  # Superposition (|0⟩ - |1⟩)/√2

# Applying gates
q0.h()  # Hadamard gate
q0.x(0.5)  # Half rotation around X-axis

# Measurement
result = q0.measure()
print(f"Measurement result: {result}")

# State visualization
print(q0.as_bracket_string())
print(q0.draw_circuit())
```

#### Multi-Qubit Systems and Entanglement

```python
from src.ariquantum import QuantumRegister

# Creating a 2-qubit system
qr = QuantumRegister(2, '0')

# Creating Bell state (entangled state)
qr.h(0)  # Apply Hadamard to first qubit
qr.cx(0, 1)  # Apply CNOT

# Circuit visualization
print(qr.draw_circuit(show_initial=True))

# Getting measurement statistics
counts = qr.get_counts(shots=1000)
print(f"Measurement statistics: {counts}")
```

## 📚 Key Classes and Methods

### Qubit Class

Working with single qubits:

```python
from math import pi
from src.ariquantum import Qubit

# Creating qubits
qubit0 = Qubit('0')  # From string representation
qubit1 = Qubit([0.6, 0.8])  # From state vector

# Basic operations
qubit0.h()  # Hadamard gate
qubit0.x()  # Pauli-X gate
qubit0.ry(pi / 4)  # Rotation around Y-axis

# State analysis
probs = qubit0.measure_probabilities()  # Measurement probabilities
x, y, z = qubit0.bloch_coordinates()  # Bloch sphere coordinates
phi, theta = qubit0.bloch_sphere_angles(degree=True)  # Bloch sphere angles
```

### QuantumRegister Class

Working with multi-qubit systems:

```python
from src.ariquantum import QuantumRegister

# Creating quantum register
qr0 = QuantumRegister(3, '0')  # 3 qubits in |000⟩ state
qr1 = QuantumRegister(2, ['+', '-'])  # Different states for each qubit

# Applying gates
qr0.h(0)  # Single-qubit operations
qr0.cx(0, 1)  # Controlled operations
qr0.ccx(0, 1, 2)  # Toffoli gate
qr0.swap(0, 1)  # State swap

# Measurements and analysis
result = qr.measure([0, 2])  # Measuring selected qubits
counts = qr.get_counts(shots=5000)  # Measurement statistics
```

## 🎯 Implementation Features

- **Deferred measurement**: Ability to continue operations with unmeasured qubits
- **Flexible initialization**: Support for various initial state formats
- **Visualization**: Text representation of circuits and states
- **Complete documentation**: Detailed descriptions of all methods and parameters
- **Optimization**: Efficient computations for multi-qubit systems

## 📊 Example Output

### Circuit Visualization

```
      ┌───┐       ┌─────────┐ ┌───────┐ ┌───┐             
q0 : ─│ H │───◯───│ X^-0.25 │─│ X^0.5 │─│ ↗ │═══●═════════ :
      └───┘   │   └─────────┘ └───╥───┘ └───┘   ║         
              │   ┌───┐ ┌───┐     ║             ║         
q1 : ─────────┼───│ H │─│ ↗ │═════●═══════●═════╬═════════ :
              │   └───┘ └───┘             ║     ║         
              │                         ┌─╨─┐ ┌─╨─┐ ┌───┐ 
q2 : ─────────┼─────────────────────────│ X │─│ X │─│ X │─ :
              │                         └─╥─┘ └───┘ └─╥─┘ 
              │   ┌───┐ ┌───┐             ║           ║   
q3 : ─────────┼───│ H │─│ ↗ │═════●═══════●═══════════╬═══ :
              │   └───┘ └───┘     ║                   ║   
            ┌─┴─┐             ┌───╨───┐ ┌───┐         ║   
q4 : ───────│ X │─────────────│ X^0.5 │─│ ↗ │═════════●═══ :
            └───┘             └───────┘ └───┘             
```

### State Representation

```
0.7071|00⟩ + 0.7071|11⟩
```

### Bloch Sphere Coordinates

```
Coordinates: (0.8660, 0.0000, 0.5000)
Angles: φ = 0.00°, θ = 60.00°
```

## 📄 License

This project is distributed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 💬 Feedback

If you have questions or suggestions, email us at: arimshcherbakov@gmail.com

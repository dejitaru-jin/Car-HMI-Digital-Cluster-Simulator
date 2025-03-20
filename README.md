# Car HMI Emulator

A Python-based dashboard emulator for car Human-Machine Interface (HMI) with multiple interactive components.

## Features

- **RPM Gauge**: Displays engine RPM with color-coded indicators
- **Speed Gauge**: Shows current speed with smooth transitions
- **Fuel Gauge**: Monitors fuel level with warning indicators
- **Clock Widget**: Shows current time in both analog and digital formats
- **Media Player**: Displays and controls music playback
- **Notification Center**: Shows system messages with priority coding

## Project Structure

```
car_hmi_emulator/
│
├── main.py                  # Entry point with main loop
│
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── component.py         # Base Component class
│   ├── constants.py         # Screen dimensions, colors, etc.
│   └── utils.py             # Utility functions
│
├── components/              # Dashboard components
│   ├── __init__.py
│   ├── gauges/              # Gauge-style components
│   │   ├── __init__.py
│   │   ├── rpm_gauge.py
│   │   ├── speed_gauge.py
│   │   └── fuel_gauge.py
│   │
│   └── info/                # Information display components
│       ├── __init__.py
│       ├── clock_widget.py
│       ├── media_widget.py
│       └── messages_widget.py
│
└── assets/                  # Assets (if needed in the future)
    ├── fonts/
    └── images/
```

## Requirements

- Python 3.6+
- Pygame

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install pygame
   ```

## Usage

Run the emulator:

```
python main.py
```

## Data Input

Each component can receive data through:

1. **Simulation Mode**: Auto-generates realistic data
2. **Socket Interface**: Each component can listen on a socket for external data input

## Key Controls

- **ESC**: Exit the application

## Extending

To add new components:

1. Create a new class that inherits from `Component`
2. Implement the required methods (`draw`, `update`)
3. Add the component to the main loop

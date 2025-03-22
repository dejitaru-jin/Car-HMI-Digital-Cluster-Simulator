# Car HMI Emulator - Design Document

## 1. Overview

The Car HMI Emulator is a simulation system that replicates a modern vehicle dashboard interface. It provides a platform for testing, demonstration, and development of automotive Human-Machine Interface (HMI) components without requiring access to actual vehicle hardware.

### 1.1 Purpose

This emulator serves the following purposes:
- Provide a visual representation of vehicle dashboard components
- Simulate realistic vehicle data patterns
- Allow for testing of UI components with simulated data
- Enable development and experimentation of dashboard layouts and features
- Serve as a learning tool for automotive HMI design

### 1.2 Scope

The emulator includes:
- Core instrument cluster gauges (RPM, speed, fuel level)
- Informational widgets (clock, media player, notification messages)
- Realistic data emulation for all components
- Configurable layout and component placement
- Socket-based communication between data sources and visual components

## 2. Architecture

The system uses a client-server architecture where each dashboard component (client) connects to a corresponding data emulator (server). This design enables:
- Independent data generation for each component
- Realistic simulation of vehicle data patterns
- Potential future integration with real vehicle data sources

### 2.1 High-Level Architecture

The application consists of three main layers:
1. **Presentation Layer**: Visual components rendered using Pygame
2. **Communication Layer**: Socket-based data transfer between components
3. **Data Layer**: Emulators that generate realistic vehicle data

### 2.2 Component Architecture

Each visual component follows a common structure:
- Inherits from a base Component class
- Connects to a data source via socket
- Updates its state based on received data
- Renders itself using Pygame primitives

Each data emulator follows a common structure:
- Inherits from a base DataEmulatorBase class
- Runs in a separate thread
- Generates realistic data patterns based on configurable behaviors
- Sends data via socket to connected components

## 3. Component Design

### 3.1 Core Components

#### 3.1.1 Base Component
The `Component` class provides:
- Region management for component placement
- Background drawing with title
- Socket connection handling
- Common update/draw lifecycle methods

#### 3.1.2 DataSource
The `DataSource` class provides:
- Socket connection to data emulators
- Automatic reconnection handling
- Data reception and callback mechanism

#### 3.1.3 DataEmulatorBase
The `DataEmulatorBase` class provides:
- Socket server creation and management
- Threading for continuous data generation
- Data queuing

### 3.2 Gauge Components

#### 3.2.1 RPM Gauge
- Displays engine RPM with analog gauge
- Color-coded needle based on RPM range
- Highlighted redline area
- Numerical RPM display

#### 3.2.2 Speed Gauge
- Displays vehicle speed with analog gauge
- Color-coded needle based on speed range
- High-speed warning area
- Digital speed display

#### 3.2.3 Fuel Gauge
- Displays fuel level percentage and liters
- Low fuel warning area and color indication
- Fuel pump icon
- 'E' and 'F' markings

### 3.3 Information Components

#### 3.3.1 Clock Widget
- Displays both analog and digital clock
- Configurable display options
- Date display
- Real-time updates

#### 3.3.2 Media Widget
- Displays current media playback information
- Track title, artist, and album
- Playback control indicators
- Progress bar and time display
- Volume level indicator

#### 3.3.3 Messages Widget
- Displays notification messages by priority
- Color-coded by severity (info, warning, critical)
- Auto-dismissal based on priority
- Timestamp display

## 4. Data Emulation

Each component has a corresponding emulator that generates realistic data patterns:

### 4.1 RPM Emulator
- Simulates engine RPM behavior
- Models idle, acceleration, cruising, and deceleration states
- Realistic transitions between states

### 4.2 Speed Emulator
- Simulates vehicle speed behavior
- Models stopped, accelerating, cruising, decelerating, and braking states
- Smooth transitions and realistic physics

### 4.3 Fuel Emulator
- Simulates fuel level changes
- Gradual consumption with random variations
- Refill events

### 4.4 Clock Emulator
- Provides real-time clock data
- Supports various time and date formats

### 4.5 Media Emulator
- Simulates media player behavior
- Track progression and playlist management
- Playback states and controls

### 4.6 Messages Emulator
- Generates notification messages of varying priorities
- Auto-dismissal based on message type
- Realistic message generation patterns

## 5. Communication Protocol

The system uses TCP sockets for communication between components and their data sources:

- Each emulator runs a socket server on a unique port
- Components connect as clients to their respective data sources
- Data is transferred as text (plain values or JSON)
- Connection handling includes automatic reconnection

Port assignments:
- RPM Emulator: 5001
- Speed Emulator: 5002
- Fuel Emulator: 5003
- Clock Emulator: 5004
- Media Emulator: 5005
- Messages Emulator: 5006

## 6. User Interface

The emulator UI is divided into a 3×2 grid, with each cell containing a specific component:

**Top row (left to right):**
- RPM Gauge
- Speed Gauge
- Fuel Gauge

**Bottom row (left to right):**
- Clock Widget
- Media Player Widget
- Messages/Notifications Widget

## 7. Future Enhancements

Potential future enhancements include:

### 7.1 Additional Components
- Navigation/GPS display
- Temperature and climate controls
- Vehicle status indicators (doors, lights, etc.)
- Driver assistance system displays

### 7.2 External Integration
- OBD-II data integration for real vehicle connection
- CAN bus simulation
- Mobile device connectivity

### 7.3 UI Improvements
- Themes and color schemes
- Configurable layouts
- 3D rendering for more realistic gauges
- Touch interface simulation

### 7.4 Extended Functionality
- Recording and playback of data patterns
- Scripted testing scenarios
- Performance benchmarking

## 8. Technical Requirements

- Python 3.7+
- Pygame 2.0+
- Standard library modules (socket, threading, json, time)
- Graphics adapter with support for hardware acceleration

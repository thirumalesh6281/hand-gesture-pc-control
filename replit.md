# Overview

This is a computer vision-based gesture control system that uses hand tracking to control desktop interactions. The application captures video from a webcam, tracks hand landmarks using MediaPipe, and translates hand gestures into mouse movements, clicks, and scrolls. It includes a demo mode that falls back to hand tracking visualization when system control libraries are unavailable.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

**Computer Vision Pipeline**: Built on OpenCV for camera capture and MediaPipe for real-time hand landmark detection. Uses a single-hand tracking model with configurable confidence thresholds for robust gesture recognition.

**Gesture Recognition Engine**: Implements a state-based gesture classifier that interprets hand positions and finger configurations to identify mouse actions (movement, clicking, scrolling). Includes debouncing mechanisms to prevent unwanted repeated actions.

**System Control Interface**: Uses PyAutoGUI for desktop automation when available, with graceful fallback to demo mode for environments where system control is restricted or unavailable.

**Real-time Processing**: Designed for low-latency interaction with smoothing algorithms to reduce jitter in cursor movement and gesture detection.

## Design Patterns

**Graceful Degradation**: The system automatically detects PyAutoGUI availability and switches to demo mode if system control libraries fail to load, ensuring the application remains functional for development and testing.

**State Management**: Implements debouncing for gesture recognition to prevent accidental triggers and maintain smooth user interaction.

**Coordinate Mapping**: Translates camera frame coordinates to screen coordinates, allowing hand movements in the camera's field of view to control the entire desktop.

# External Dependencies

## Computer Vision Libraries
- **OpenCV (cv2)**: Camera capture, image processing, and video display
- **MediaPipe**: Google's hand landmark detection and tracking solution

## System Control
- **PyAutoGUI**: Desktop automation for mouse control and screen interaction (optional, falls back to demo mode if unavailable)

## Core Python Libraries
- **NumPy**: Numerical computations for coordinate transformations and gesture calculations
- **Time**: Debouncing and timing control for gesture recognition
- **OS**: System-level operations and environment detection

## Hardware Requirements
- **Webcam**: Video capture device for hand tracking input
- **Display**: Target screen for cursor control and gesture interaction
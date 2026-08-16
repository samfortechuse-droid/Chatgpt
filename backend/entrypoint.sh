#!/bin/bash

# Start Virtual Framebuffer
Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp &
export DISPLAY=:99

# Start Window Manager
fluxbox &

# Start VNC Server (No password, shared for multi-access)
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 &

# Start noVNC Websockify proxy
websockify --web=/usr/share/novnc/ 6080 localhost:5900 &

# Start FastAPI Application
uvicorn main:app --host 0.0.0.0 --port 8000 --ws-ping-interval 10 --ws-ping-timeout 30

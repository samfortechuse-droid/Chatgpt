FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Install VNC and noVNC for live streaming and human interaction
RUN apt-get update && apt-get install -y \
    xvfb x11vnc websockify novnc fluxbox \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose FastAPI (8000) and noVNC (6080)
EXPOSE 8000 6080

CMD ["/app/entrypoint.sh"]

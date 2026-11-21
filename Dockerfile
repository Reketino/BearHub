
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV XDG_CACHE_HOME=/tmp/.cache
ENV FONTCONFIG_CACHE_DIR=/tmp/.cache/fontconfig

WORKDIR /app

# Create writable Fontconfig cache directory
RUN mkdir -p /tmp/.cache/fontconfig \
    && chmod -R 777 /tmp/.cache

# System dependencies for PySide6, X11 and evdev
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    linux-libc-dev \
    libgl1 \
    libegl1 \
    libdbus-1-3 \
    libfontconfig1 \
    libglib2.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxtst6 \
    libxdo3 \
    xdotool \
    x11-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and assets
COPY src/ ./src/
COPY assets/ ./assets/

ENV PYTHONPATH=/app/src
ENV QT_QPA_PLATFORM=xcb

CMD ["python", "src/main.py"]

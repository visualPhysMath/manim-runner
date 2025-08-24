FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    MANIM_RENDERER=cairo

# ランタイム + ビルドに必要な最小セット
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libglib2.0-0 \
    fonts-dejavu-core \
    # ここからビルド系
    build-essential pkg-config libffi-dev python3-dev \
    && rm -rf /var/lib/apt/lists/*

# pip周りを先に最新化（ビルドの安定性向上）
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Manim をピン留め（0.18系の安定版）
RUN pip install --no-cache-dir "manim==0.18.1"

WORKDIR /work
CMD ["bash","-lc","python -V"]

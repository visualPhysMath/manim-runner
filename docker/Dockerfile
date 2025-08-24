FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    MANIM_RENDERER=cairo

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libcairo2 libpango-1.0-0 libpangocairo-1.0-0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "manim>=0.18,<0.19"

WORKDIR /work
CMD ["bash","-lc","python -V"]

# 🚀 Deployment Guide

This guide explains how to deploy the Multi-Modal AI Generator to various platforms and enable cross-device access.

## 🐳 Docker Deployment

The application is containerized for easy deployment on any system with Docker and NVIDIA GPU support.

### Prerequisites
- Docker installed
- NVIDIA GPU with drivers installed
- NVIDIA Container Toolkit installed

### 1. Build the Image
```bash
docker build -t ai-generator .
```

### 2. Run the Container
```bash
docker run -d \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/.cache:/root/.cache \
  --name ai-generator \
  ai-generator
```

- `--gpus all`: Enables GPU access
- `-p 7860:7860`: Maps port 7860
- `-v .../outputs`: Persists generated files
- `-v .../.cache`: Persists downloaded models (saves re-downloading)

## ☁️ Cloud Deployment (Hugging Face Spaces)

This application is ready to be deployed to Hugging Face Spaces using Docker.

1. Create a new Space on Hugging Face.
2. Select **Docker** as the SDK.
3. Choose a GPU hardware (e.g., Nvidia T4 or A10G).
4. Upload the repository contents (including `Dockerfile`).
5. The Space will build and launch automatically.

## 🔐 Environment Variables

Configure the application using these environment variables (pass with `-e` in Docker or set in Spaces settings):

| Variable | Description | Default |
|----------|-------------|---------|
| `GRADIO_USERNAME` | Username for basic auth | None (Public) |
| `GRADIO_PASSWORD` | Password for basic auth | None |
| `GRADIO_SHARE` | Set to `true` for a temporary public URL | `False` |
| `GRADIO_SERVER_PORT`| Port to run on | `7860` |

### Example: Protected Deployment
```bash
docker run -d --gpus all -p 7860:7860 \
  -e GRADIO_USERNAME=admin \
  -e GRADIO_PASSWORD=secure_password \
  ai-generator
```

## 📱 Mobile Access

The interface is optimized for mobile devices. To access it from your phone:

**Option 1: Local Network**
1. Run the app on your PC.
2. Find your PC's IP address (e.g., `192.168.1.5`).
3. Open `http://192.168.1.5:7860` on your phone browser.

**Option 2: Public Share**
1. Run with `GRADIO_SHARE=true`.
2. Use the provided `*.gradio.live` link.

**Option 3: Cloud**
1. Deploy to Hugging Face Spaces.
2. Access the Space URL on your phone.

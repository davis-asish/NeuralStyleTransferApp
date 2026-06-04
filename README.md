<![CDATA[<div align="center">

# 🎨 NeuralStyleTransferApp

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

**Local AI image generator and multi-style transfer powered by Stable Diffusion Turbo.**  
No API keys. No cloud. Runs entirely on your machine.

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Text-to-Image** | Generate images from text prompts via `stabilityai/sd-turbo` |
| 🎭 **Style Transfer** | Transform any image into 6 artistic presets |
| 💻 **100% Local** | All inference on-device — no Replicate, no OpenAI, no billing |
| ⚡ **GPU / CPU** | Auto-detects CUDA; gracefully falls back to CPU |
| 🐳 **Docker Ready** | One command to run the full stack in a container |
| 📥 **Download** | Save generated and stylized images directly from the browser |

### Style Presets
`Anime` · `Cartoon` · `Oil Painting` · `Sketch` · `Cyberpunk` · `Realistic`

---

## 🚀 Quick Start

### Option A — Local Python

```bash
git clone https://github.com/davis-asish/NeuralStyleTransferApp.git
cd NeuralStyleTransferApp

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
python backend/app.py
```

Open **http://localhost:5000** in your browser.

> **Note:** First run downloads the SD-Turbo model (~3 GB). Ensure a stable internet connection.

---

### Option B — Docker (recommended)

```bash
git clone https://github.com/davis-asish/NeuralStyleTransferApp.git
cd NeuralStyleTransferApp

# CPU
docker build -t neural-style-app .
docker run -p 5000:5000 neural-style-app

# GPU (requires nvidia-docker)
docker run --gpus all -p 5000:5000 neural-style-app
```

Open **http://localhost:5000**.

---

## 🖥️ Usage

### Generate from a Prompt
1. Enter a descriptive text prompt — e.g. *"a neon-lit Tokyo street at midnight, cinematic"*
2. Click **Generate Image**
3. Wait 5–30 seconds depending on hardware
4. Download the result

### Stylize an Image
1. Upload a PNG, JPG, or JPEG
2. Choose a style preset from the dropdown
3. Click **Apply Style**
4. Download the stylized image

---

## 🏗️ Architecture

```
Browser
  │
  ├── GET /              → Serves index.html (HTML/CSS/JS frontend)
  ├── POST /generate     → Text-to-image (sd-turbo txt2img pipeline)
  └── POST /stylize      → Image-to-image (sd-turbo img2img pipeline)
                                  │
                           PyTorch + Diffusers
                           CUDA if available, else CPU
                                  │
                           /static/outputs/  (saved images)
```

**Stack:**
- **Backend:** Flask REST API (`backend/app.py`)
- **AI Model:** `stabilityai/sd-turbo` via Hugging Face `diffusers`
- **Frontend:** Vanilla HTML/CSS/JS with progress indicators
- **Containerization:** Docker (Python 3.11-slim base)

---

## ⚙️ System Requirements

| | Minimum | Recommended |
|-|---------|-------------|
| **RAM** | 8 GB | 16 GB |
| **VRAM** | — (CPU mode) | 4 GB (GPU mode) |
| **Storage** | 5 GB free | 10 GB free |
| **Python** | 3.8+ | 3.10+ |
| **CUDA** | Optional | 11.8+ |

---

## 📦 Key Dependencies

```
flask>=2.3.0
torch>=2.0.0
diffusers>=0.21.0
transformers>=4.30.0
accelerate>=0.20.0
Pillow>=10.0.0
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| CUDA out of memory | Switch to CPU mode or reduce image size |
| Slow generation | Use GPU if available; CPU takes 10–30s per image |
| Model download hangs | Check internet connection; model is ~3 GB |
| Port 5000 in use | Change port: `python backend/app.py --port 5001` |

---

## 📄 License

[MIT License](LICENSE) — free to use, modify, and distribute.
]]>

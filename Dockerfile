FROM python:3.11-slim

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    tesseract-ocr \
    ghostscript \
    poppler-utils \
    libglib2.0-0 \
    libgl1 \
    libxcb1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    fonts-noto-cjk \
    ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install base deps
RUN pip install --upgrade pip \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

RUN pip install requests \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

# Install torch (CPU)
RUN pip install torch==2.10.0 torchvision==0.25.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    --trusted-host download.pytorch.org \
    --trusted-host download-r2.pytorch.org \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

# Install project deps
RUN pip install -r requirements.txt \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

# Copy code
COPY . .

# HuggingFace offline mode
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1
ENV HF_HOME=/root/.cache/huggingface

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

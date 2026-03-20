FROM python:3.11-slim

WORKDIR /app

# Installing basic system tools
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get install -y libxcb1
RUN apt-get install -y libgl1
RUN apt-get install -y fonts-noto-cjk
RUN apt-get install -y libglib2.0-0

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates
    
# Copying dependency list 
COPY requirements.txt .

RUN pip install requests \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

RUN pip install torch==2.10.0 torchvision==0.25.0 \
    --index-url https://download.pytorch.org/whl/cpu \
    --trusted-host download.pytorch.org \
    --trusted-host download-r2.pytorch.org \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org

RUN pip install -r requirements.txt \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org


# Copying project code
COPY . .

# Forcing offline HuggingFace mode
ENV TRANSFORMERS_OFFLINE=1
ENV HF_HUB_OFFLINE=1
ENV HF_HOME=/root/.cache/huggingface

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

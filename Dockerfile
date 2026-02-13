# Base image
FROM python:3.10-slim

# System dependencies install karna (FFmpeg aur MediaInfo)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Working directory set karna
WORKDIR /app

# Sabhi files copy karna
COPY . .

# Python libraries install karna
RUN pip install --no-cache-dir -r requirements.txt

# Environment variable for logs (taaki logs real-time dikhein)
ENV PYTHONUNBUFFERED=1

# Bot aur Dummy server start karne ke liye (run.py dono ko handle karega)
CMD ["python3", "run.py"]

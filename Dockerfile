# Base image
FROM python:3.10-slim

# System dependencies install karna
RUN apt-get update && apt-get install -y \
    ffmpeg \
    mediainfo \
    && rm -rf /var/lib/apt/lists/*

# Working directory set karna
WORKDIR /app

# Files copy karna
COPY . .

# Python libraries install karna
RUN pip install --no-cache-dir -r requirements.txt

# Start script ko permission dena
RUN chmod +x start.sh

# Bot aur Dummy server start karne ke liye
# Purane CMD ["./start.sh"] ki jagah ye likhein:
CMD ["python3", "run.py"]

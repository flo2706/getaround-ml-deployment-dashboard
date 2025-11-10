FROM python:3.12-slim

# (Optional but useful for xgboost/lightgbm/numba, etc.)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Env vars: cleaner logs, HF port, and fix for Matplotlib/Swagger
ENV PYTHONUNBUFFERED=1 \
    PORT=7860 \
    MPLCONFIGDIR=/tmp/matplotlib

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the source code
COPY . /app

# Expose API port
EXPOSE 7860

# Let the shell expand $PORT (HF provides 7860)
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port $PORT"]

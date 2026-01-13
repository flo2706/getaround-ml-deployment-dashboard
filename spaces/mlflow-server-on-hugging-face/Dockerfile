# 🐍 Base image
FROM continuumio/miniconda3

RUN apt-get update && \
    apt-get install -y nano unzip curl gcc g++
RUN conda install -y python=3.10

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip && ./aws/install

# Hugging Face requirement: create a user
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy files with correct permissions
COPY --chown=user . $HOME/app

COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# Launch MLflow server 
CMD mlflow server \
  --host 0.0.0.0 \
  --port ${PORT:-7860} \
  --serve-artifacts \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "${ARTIFACT_STORE_URI}" \
  --disable-security-middleware
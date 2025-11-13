FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install poetry

COPY . .

RUN poetry install

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# ENTRYPOINT ["poetry", "run","streamlit", "run", "app.py", "--server.port=3000", "--server.address=0.0.0.0"]
ENTRYPOINT ["sh main.sh"]

FROM python:3.12-bookworm

ENV PYTHONBUFFERED 1
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH='/'

WORKDIR /app

# Copia apenas os arquivos de definição do projeto (pyproject.toml e poetry.lock)
COPY pyproject.toml poetry.lock ./

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
       curl \
       libpq-dev \
       build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false \
    && poetry install --no-root \
    && apt-get remove -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Finalmente, copia o diretório "app" com seu código-fonte
COPY ./app /app


FROM python:3.12-slim

WORKDIR /app

# Build deps untuk scipy / numpy / scikit-learn / xgboost
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Hanya salin kode yang diperlukan
# (Firmware, notebooks, journals, data dikecualikan via .dockerignore)
COPY api/   ./api/
COPY model/ ./model/

RUN mkdir -p data model/artifacts

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8000/health || exit 1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]

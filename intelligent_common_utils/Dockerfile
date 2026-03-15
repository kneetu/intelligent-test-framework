# Multi-stage Docker build; Python 3.10 per TECH_STACK_VERSIONS
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
ENV PYTHONPATH=/app/src
COPY --from=builder /root/.local /root/.local
COPY src/ /app/src/
COPY config/ /app/config/
COPY resources/ /app/resources/
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["python", "-m", "agent_core.main", "serve"]

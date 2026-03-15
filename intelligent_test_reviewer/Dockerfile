# Build from repo root: docker build -f intelligent_test_reviewer/Dockerfile .
FROM python:3.10-slim
WORKDIR /app
COPY intelligent_common_utils/requirements.txt /app/common_requirements.txt
COPY intelligent_test_reviewer/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/common_requirements.txt -r /app/requirements.txt
ENV PYTHONPATH=/app/intelligent_common_utils/src:/app/intelligent_test_reviewer/src
COPY intelligent_common_utils/ /app/intelligent_common_utils/
COPY intelligent_test_reviewer/ /app/intelligent_test_reviewer/
CMD ["python", "-m", "reviewer_core.main", "--prd", "/app/intelligent_test_reviewer/resources/PRD.txt", "--csv", "/app/input/out.csv", "--output", "/app/output/review.json"]

FROM python:3.12-slim AS builder
WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app

ENV PATH=/usr/local/bin:${PATH}

COPY --from=builder /install /usr/local

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

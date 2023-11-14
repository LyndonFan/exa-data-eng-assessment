FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# handle nested variables
ENV MONGO_URI=$MONGO_URI
ENV PSQL_URI=$PSQL_URI

CMD ["/bin/bash", "-c", "python -m src.db.schema && python main.py data"]
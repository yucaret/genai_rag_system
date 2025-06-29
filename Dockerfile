# Use official Python image
FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements/prod.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
#RUN pip install --upgrade pip && \
#    pip install --no-deps -r requirements.txt

#RUN pip show openai && \
#    pip show openai | grep "Version: 0.28.1" || (echo "Wrong OpenAI version!" && exit 1)

# Copy project
COPY src/ ./src/
COPY config/ ./config/

#Esta linea se elimina por que se ponrdran la variables en railaway
#COPY .env.template .env

COPY src/main.py main.py

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

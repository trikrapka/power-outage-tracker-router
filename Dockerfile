FROM python:3.10

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y iputils-ping
RUN pip install -r requirements.txt

COPY src/ .

CMD ["python", "main.py"]

from python:3.10
WORKDIR /app
ADD . .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "main.py"]
FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["tail", "-f", "/dev/null"]
#CMD ["python", "app.py"]
#CMD ["gunicorn", "--worker-class", "eventlet", "--bind", "0.0.0.0:5001", "app:app"]
#CMD ["gunicorn", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "app:app"]

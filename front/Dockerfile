FROM python:3.10

RUN mkdir /frontend_dock

WORKDIR /frontend_dock

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn front:otv --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
FROM python:3.10

RUN mkdir /backend_dock

WORKDIR /backend_dock

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn start:app --workers 3 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:7419
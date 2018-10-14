FROM python:3.7

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv run pip install pip==18.0
RUN pipenv install --system --deploy

CMD ["python", "importer.py"]

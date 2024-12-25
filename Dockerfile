FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
ARG YOUR_ENV

ENV YOUR_ENV=${YOUR_ENV}

COPY app ./app
COPY data ./data
COPY geli ./geli 
COPY CA_ecr_prices.csv .
COPY pyproject.toml ./

RUN python3 -m pip install poetry

RUN poetry install

EXPOSE 8000

CMD ["poetry run uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload"]
FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
RUN pip install .

EXPOSE 8080

CMD ["python", "-m", "aiohttp.web", "-H", "0.0.0.0", "-P", "8080", "zoteroxy:init_func"]

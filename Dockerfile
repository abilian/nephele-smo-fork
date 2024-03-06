FROM python:3.11-alpine

WORKDIR /app

RUN adduser -D python
RUN chown -R python:python /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

USER python

EXPOSE 5000

COPY src/ .

CMD ["flask", "run", "--host", "0.0.0.0"]
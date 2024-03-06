FROM python:3.11

RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

WORKDIR /app

RUN adduser python
RUN chown -R python:python /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

USER python

EXPOSE 5000

COPY src/ .

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]
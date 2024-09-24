FROM python:3.11

RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

WORKDIR /app

RUN adduser python
RUN chown -R python:python /app

COPY pyproject.toml /app
COPY README.md .
COPY wsgi.py .
COPY src/ src/
RUN pip install .

USER python

ENV FLASK_RUN_PORT=8000
EXPOSE 8000

#COPY src/ .
COPY bin/hdarctl /bin/

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]

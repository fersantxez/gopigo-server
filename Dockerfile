FROM python:3.6.4-alpine3.7
MAINTAINER Fernando Sanchez "fernandosanchezmunoz@gmail.com"

COPY . /app
WORKDIR /app
RUN apk update
RUN apk upgrade
RUN apk add gcc g++ make linux-headers musl-dev libffi-dev
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["run.py"]
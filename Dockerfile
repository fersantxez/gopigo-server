FROM python:3.6.4-alpine3.7
MAINTAINER Fernando Sanchez "fernandosanchezmunoz@gmail.com"

RUN apk update
RUN apk upgrade
RUN apk add gcc g++ make linux-headers musl-dev libffi-dev raspberrypi-libs
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
#ENTRYPOINT ["python"]
#CMD ["run.py"]
CMD modprobe i2c-dev && python run.py
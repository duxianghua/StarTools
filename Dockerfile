FROM alpine:3.9
COPY . /var/app

WORKDIR /var/app

CMD [ "python" ]

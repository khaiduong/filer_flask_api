FROM alpine

MAINTAINER Khai Duong <qkhai20@gmail.com>

RUN apk add --update py-pip

# application folder
ENV APP_DIR /filer_app


# SRC dir
RUN mkdir ${APP_DIR}

# expose web server port
# only http, for ssl use reverse proxy
EXPOSE 8000

# Install requirements
COPY ./src ${APP_DIR}/src
COPY ./filer ${APP_DIR}/filer
COPY ./storage ${APP_DIR}/storage
WORKDIR ${APP_DIR}
RUN pip install --upgrade pip && pip install -r src/requirements.txt
RUN chmod 777 -R ${APP_DIR}

# exectute start up script
ENTRYPOINT [ "python" ]
CMD [ "src/server.py" ]

## FRONTEND BUILD STAGE

FROM node:14-bullseye as frontend-build-stage

WORKDIR /frontend
ADD frontend/package*.json ./
RUN npm install
ADD frontend .
RUN npm run build

# BACKEND BUILD STAGE

FROM python:3.9-alpine3.14 as base-server

RUN apk --no-cache add git \
    curl \
    build-base \
    libffi-dev \
    openssl-dev \
    cargo

## Magic Castle User
RUN adduser -D mcu

# Set mcu as the owner of the SQLite database volume
RUN mkdir -p /home/mcu/database && chown -R mcu:mcu /home/mcu/database

# Set mcu as the owner of the credentials directory
RUN mkdir -p /home/mcu/credentials && chown -R mcu:mcu /home/mcu/credentials

USER mcu
WORKDIR /home/mcu
RUN mkdir /home/mcu/mchub
RUN mkdir /home/mcu/tests

## Python requirements
ADD poetry.lock pyproject.toml /home/mcu/
RUN python3 -m venv /home/mcu/venv
ENV VIRTUAL_ENV=/home/mcu/venv
RUN /home/mcu/venv/bin/pip install poetry
RUN /home/mcu/venv/bin/poetry install

## Python backend src
ADD mchub /home/mcu/mchub
ADD tests /home/mcu/tests

FROM base-server as cleanup-daemon

CMD /home/mcu/venv/bin/python -m mchub.services.cull_expired_cluster

## PRODUCTION IMAGE
FROM base-server as production-server

ENV TERRAFORM_VERSION 1.1.6

## EXTERNAL DEPENDENCIES

# Terraform
USER root
RUN case "$(apk --print-arch)" in \
    aarch64) export TERRAFORM_URL="https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_arm64.zip" ;; \
    x86_64) export TERRAFORM_URL="https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" ;; \
    esac; \
    curl -L ${TERRAFORM_URL} -o terraform.zip && \
    unzip terraform.zip -d /usr/local/bin && \
    rm terraform.zip

USER mcu
RUN mkdir /home/mcu/clusters

ADD .terraformrc /home/mcu
RUN mkdir -p /home/mcu/.terraform.d/plugin-cache

## Vue Js frontend src
COPY --from=frontend-build-stage /frontend/dist /home/mcu/dist

ENV OS_CLIENT_CONFIG_FILE=/home/mcu/credentials/clouds.yaml
ENV MAGIC_CASTLE_PATH=../../magic_castle
ENV MAGIC_CASTLE_VERSION=11.8

RUN curl -L https://github.com/ComputeCanada/magic_castle/releases/download/${MAGIC_CASTLE_VERSION}/magic_castle-openstack-${MAGIC_CASTLE_VERSION}.tar.gz -o magic_castle.tar.gz && \
    tar xvf magic_castle.tar.gz && \
    mv magic_castle-* /home/mcu/magic_castle && \
    rm magic_castle.tar.gz

CMD /home/mcu/venv/bin/python -m gunicorn --workers 5 --bind 0.0.0.0:5000 --worker-class gevent "mchub:create_app()"
#CMD /home/mcu/venv/bin/python -m mchub.wsgi

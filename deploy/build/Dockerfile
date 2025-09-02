FROM python:3.12.6-slim-bullseye
LABEL maintainer="Hftech_"

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux


ARG ENVIRONMENT

ENV ENVIRONMENT=${ENVIRONMENT} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYTHONPATH=/usr/src/app

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye main contrib non-free" >/etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >>/etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bullseye-backports main contrib non-free" >>/etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security bullseye-security main contrib non-free" >>/etc/apt/sources.list

RUN apt-get update -y \
    && apt-get upgrade -y \
    build-essential \
    gcc \
    libpq-dev \
    locales \
    git \
    && apt-get install -y iputils-ping \
    && apt-get install -y pkg-config libxml2-dev libxmlsec1-dev libxmlsec1-openssl \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen

RUN locale-gen en_US.UTF-8

# set work directory
WORKDIR /usr/src/

RUN adduser worker
USER worker
# install dependencies
COPY --chown=worker:worker requirements.txt /usr/src/requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  --upgrade pip
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/  -r requirements.txt

USER root
RUN apt purge -y gcc

USER worker

ENV PATH="/home/worker/.local/bin:${PATH}"


COPY fapi-init.sh /usr/local/bin/fapi-init.sh


EXPOSE 80

ENTRYPOINT [ "fapi-init.sh" ]


# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
# CMD ["fastapi", "run", "app/main.py", "--port", "80"]


FROM python:3.8

RUN cat /etc/issue

RUN pip3 install --upgrade pip

COPY ./requirements.txt ./app/requirements.txt

# install requirements
RUN pip3 install -r ./app/requirements.txt

RUN rm -r /root/.cache

# copy files and start
COPY . /app

WORKDIR /app

CMD ['bash']
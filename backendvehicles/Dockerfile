FROM python:3.8

RUN cat /etc/issue

RUN pip3 install --upgrade pip

COPY ./requirements.txt ./backendvehicles/requirements.txt

# install requirements
RUN pip3 install -r ./backendvehicles/requirements.txt

RUN rm -r /root/.cache

# copy files and start
COPY . /backendvehicles

WORKDIR /backendvehicles

CMD ['bash']
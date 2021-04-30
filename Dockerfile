FROM python:3

ENV DB_URI=/tmp/vlandb.db

WORKDIR /usr/src/app

COPY . .

#COPY setup.py /usr/src/app
#COPY requirements.txt /usr/src/app
#COPY networkapp/ /usr/src/network/app
RUN python3 -m pip install --upgrade pip
RUN pip install .




CMD [ "vlan-controller"]
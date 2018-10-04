FROM docker

RUN apk add --no-cache python3

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY dockermirror/ dockermirror/

VOLUME /var/spool/docker-mirror

ENV FLASK_APP=dockermirror.api.app
ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]

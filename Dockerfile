FROM docker

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dockermirror/ dockermirror/

VOLUME /var/spool/dockermirror

ENTRYPOINT ["python3", "-m", "dockermirror"]

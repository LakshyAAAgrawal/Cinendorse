FROM ubuntu:18.04
RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
ADD requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

ADD ./main.py /app/main.py
ADD ./server /app/server
ADD ./Recommendation /app/Recommendation


#ENTRYPOINT [ "gunicorn", "main:app" ]
CMD gunicorn --bind 0.0.0.0:$PORT main:app

FROM python:3.11.6-slim

WORKDIR /usr/src/app
EXPOSE 5000

COPY requirements.txt ./

RUN mkdir data
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD [ "python", "./main.py" ]
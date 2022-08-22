FROM python:3.7
# run this before copying requirements for cache efficiency
ENV FLASK_APP="mailer.server:create_app()"
ENV PYTHONUNBUFFERED=1
RUN apt-get update -y
RUN apt-get install build-essential
RUN apt-get install default-libmysqlclient-dev
RUN pip install mysqlclient
RUN pip install --upgrade pip

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mailer .
EXPOSE 8088
CMD flask run -h 0.0.0.0 -p 8088
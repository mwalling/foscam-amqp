FROM python:3.7
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install --no-cache --requirement requirements.txt
USER nobody
CMD python /config/config.ini

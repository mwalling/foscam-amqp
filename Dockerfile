FROM python:3.7
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install --no-cache --requirement requirements.txt
ADD . /app/
USER nobody
CMD python foscam_control.py /config/config.ini

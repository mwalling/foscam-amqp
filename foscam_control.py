#!/usr/bin/env python

import configparser
import logging
import sys
import time

import pika
import requests

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Camera = namedtuple('Camera', ['ip', 'port', 'username', 'password'])
class Camera(object):
    def __init__(self, name, ip, port, username, password, **kwargs):
        self.name = name
        self.password = password
        self.username = username
        self.port = port
        self.ip = ip

    def __str__(self):
        return self.name

    def api_call(self, cmd, **extra):
        params = {'usr': self.username,
                  'pwd': self.password,
                  'cmd': cmd}
        params = {**params, **extra}
        url = f'https://{self.ip}:{self.port}/cgi-bin/CGIProxy.fcgi'
        logger.debug('Performing request to url %s with params %r', url, params)
        requests.get(url, params=params, verify=False)

    def perform_move(self, direction: str, duration):
        cmd = f'ptzMove{direction.title()}'
        self.api_call(cmd)
        time.sleep(duration)
        self.api_call('ptzStopRun')


class FoscamControl(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.channel = None
        self.config = configparser.ConfigParser()

    def run(self):
        self.config.read(self.config_file)
        self.connect()
        self.channel.basic_consume(queue='foscammove', auto_ack=True, on_message_callback=self.callback)
        logger.info('Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def connect(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.config['default']['broker_address']))
        self.channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()
        self.channel.queue_declare('foscammove')
        self.channel.queue_bind('foscammove', 'amq.topic', 'foscammove.#')

    def callback(self, ch: pika.adapters.blocking_connection.BlockingChannel, method: pika.spec.Basic.Deliver,
                 properties: pika.spec.BasicProperties, body: bytes):
        camera = self.get_camera(method.routing_key)
        if camera is None:
            logger.warning('Could not locate camera config for [%s]', method.routing_key)
            return
        action = body.decode('utf-8')
        logger.info('Got action [%s] for camera [%s]', action, camera)
        if action.startswith('move_'):
            direction = action[5:]
            if direction in ('up', 'down'):
                duration = 0.5
            else:
                duration = 1.5
            try:
                camera.perform_move(direction, duration)
            except Exception as e:
                logger.exception('Error performing action', exc_info=e)

    def get_camera(self, routing_key: str):
        camera_name = routing_key.rsplit('.', 1)[-1]
        if not self.config.has_section(camera_name):
            return None
        return Camera(camera_name, **self.config[camera_name])


if __name__ == '__main__':
    control = FoscamControl('config.ini')
    control.run()

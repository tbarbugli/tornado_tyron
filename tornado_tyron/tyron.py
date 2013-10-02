from collections import defaultdict
from collections import deque
import copy
import json
import logging
import redis
import threading
import time
from tornado import ioloop
from tornado import web
from tornado.options import define
from tornado.options import options
import weakref


define("pubsub_channel", default="tyron_pubsub", help="Redis pub/sub channel")
define("redis_hostname", default="localhost", help="Redis host address")
define("redis_port", default=6379, help="Redis host port")
define("redis_db", default=0, help="Redis host db")
define("redis_password", default=0, help="Redis password")
define("webserver_port", default=8080, help="Webserver port")
define("timeout", default=600, help="Connections timeout")


io_loop = ioloop.IOLoop.instance()
app_logger = logging.getLogger("tornado.application")

def get_redis_connection():
    return redis.Redis(
        options.redis_hostname,
        options.redis_port,
        options.redis_db,
        options.redis_password
    )

def wrap_callback(callback, handler, channel, *args):
    def wrapper():
        handler.subscriptions[channel].remove(callback)
        timeout = handler.timeouts.pop(callback, None)
        if timeout is not None:
            io_loop.remove_timeout(timeout)
        if callback():
            callback()(*args)
    return wrapper

class RedisSub(threading.Thread):
    """
    subscribes to a redis pubsub channel and routes
    messages to subscribers

    messages have this format
    {'channel': ..., 'data': ...}

    """

    def __init__(self, pubsub_channel, timeout):
        threading.Thread.__init__(self)
        self.pubsub_channel = pubsub_channel
        self.subscriptions = defaultdict(deque)
        self.timeouts = {}
        self.timeout = timeout

    def add_subscription(self, channel, callback):
        callback_ref = weakref.ref(callback)
        deadline = int(time.time() + self.timeout)
        timeout = io_loop.add_timeout(
            deadline,
            wrap_callback(callback_ref, self, channel)
        )
        self.timeouts[callback_ref] = timeout
        self.subscriptions[channel].appendleft(callback_ref)

    def decode_message(self, message):
        return json.loads(message)

    def parse_message(self, message):
        msg = self.decode_message(message['data'])
        return msg['channel'], msg['data']

    def notify(self, channel, data):
        if self.subscriptions[channel]:
            app_logger.info('got a message on channel %s, %d client subscribed' % (channel, len(self.subscriptions[channel])))

        callbacks = copy.copy(self.subscriptions[channel])
        for callback in callbacks:
            callback = wrap_callback(callback, self, channel, data)
            io_loop.add_callback(callback)

    def listen(self):
        client = get_redis_connection()
        pubsub = client.pubsub()
        pubsub.subscribe(self.pubsub_channel)
        for message in pubsub.listen():
            if message['type'] != 'message':
                continue
            self.notify(*self.parse_message(message))

    def run(self):
        self.listen()


class SubscribeHandler(web.RequestHandler):

    def __call__(self, chunk=None):
        self.finish(chunk)

    @web.asynchronous
    def get(self, channel):
        self.application.pubsub.add_subscription(
            channel=channel,
            callback=self
        )

    post = get

class RedisStore(web.RequestHandler):

    def get(self, key):
        self.finish(self.application.redis.get(key))

    post = get

class HealthCheck(web.RequestHandler):

    def get(self):
        self.finish('OK')

def start_pubsub_thread():
    pubsub = RedisSub(
        pubsub_channel=options.pubsub_channel,
        timeout=options.timeout
    )
    pubsub.daemon = True
    pubsub.start()
    return pubsub

def main():
    options.parse_command_line()
    application = web.Application([
        (r"/health/", HealthCheck),
        (r"/store/(.*)/", RedisStore),
        (r"/(.*)/", SubscribeHandler),
    ])
    application.pubsub = start_pubsub_thread()
    application.redis = get_redis_connection()
    application.listen(options.webserver_port)
    io_loop.start()

if __name__ == '__main__':
    main()

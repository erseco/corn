from kombu import Connection, Exchange, Queue, Consumer
from kombu.utils.compat import nested


class CornWorker(object):

    def __init__(self, app):
        self.app = app

    def start(self):
        queues = []
        for queue, routing_key, function in self.app.queues:
            exchange = Exchange(
                self.app.conf.EXCHANGE_NAME, 'topic', durable=True)
            queue_name = '{}_{}'.format(
                self.app.SERVICE_NAME,
                queue)
            queue = Queue(
                queue_name, exchange=exchange, routing_key=routing_key)
            queues.append((queue, function))
        with Connection(self.app.conf.BROKER_URL) as connection:
            with connection.channel() as channel:
                consumers = []
                for queue, function in queues:
                    consumer = Consumer(channel, queue, callback=function, accept=['json'])
                    consumers.append(consumer)
                with nested(*consumers):
                        connection.drain_events(timeout=1)

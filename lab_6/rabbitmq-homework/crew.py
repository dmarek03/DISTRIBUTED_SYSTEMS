import json
from dataclasses import dataclass
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from threading import Thread
from message import Message, SenderType
from configuration import exchange_orders, exchange_deliveries, exchange_admin_in, exchange_admin_out


@dataclass
class Crew:
    name: str | None = None
    connection_in: BlockingConnection | None = None
    connection_out: BlockingConnection | None = None
    channel_in: BlockingChannel | None = None
    channel_out: BlockingChannel | None = None
    queue_name: str | None = None

    def setup_connection(self) -> None:
        self.name = input("Enter crew name:")
        self.connection_in = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost"),
        )

        self.connection_out = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost"),
        )

        self.channel_in = self.connection_in.channel()
        self.channel_out = self.connection_out.channel()

        self.channel_in.exchange_declare(exchange=exchange_deliveries, exchange_type="topic")
        self.channel_in.exchange_declare(exchange=exchange_admin_out, exchange_type="topic")
        self.channel_out.exchange_declare(exchange=exchange_orders, exchange_type="topic")

        result = self.channel_in.queue_declare('', exclusive=True)
        self.queue_name = result.method.queue

        self.channel_in.queue_bind(queue=self.queue_name, exchange=exchange_deliveries, routing_key=self.name)
        self.channel_in.queue_bind(queue=self.queue_name, exchange=exchange_admin_out, routing_key="all.*")
        self.channel_in.queue_bind(queue=self.queue_name, exchange=exchange_admin_out, routing_key="crew.*")

    def place_order(self) -> None:
        while True:

            items_to_order = input("Enter items to order: ")
            for item in items_to_order.split(","):
                item = item.strip()
                message = Message(sender=self.name, sender_type=SenderType.CREW, body=item)
                self.channel_out.basic_publish(exchange=exchange_orders, routing_key=item,
                                               body=json.dumps(message.to_dict()))

                print(f"Sent order for: {item}")
                self.send_info_to_admin(message)

    def send_info_to_admin(self, message: Message):

        self.channel_out.basic_publish(exchange=exchange_admin_in, routing_key="admin.crew_info",
                                       body=json.dumps(message.to_dict()))

    def wait_for_delivery(self) -> None:
        self.channel_in.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True
        )

        self.channel_in.start_consuming()

    @staticmethod
    def callback(ch, method, properties, body):

        data = json.loads(body.decode())
        sender = data['sender']
        sender_type = data['sender_type']
        message = data['body']

        routing_key = method.routing_key

        print(f"\n[{routing_key}] From {sender_type}:{sender} – {message}")


def main() -> None:
    crew = Crew()
    crew.setup_connection()

    Thread(target=crew.wait_for_delivery, daemon=True).start()
    crew.place_order()


if __name__ == '__main__':
    main()


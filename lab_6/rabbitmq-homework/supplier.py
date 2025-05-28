import json
from dataclasses import dataclass
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from threading import Thread
from message import Message, SenderType
from configuration import exchange_orders, exchange_deliveries, exchange_admin_in, exchange_admin_out


@dataclass
class Supplier:
    name: str | None = None
    connection_in: BlockingConnection | None = None
    connection_out: BlockingConnection | None = None
    channel_in: BlockingChannel | None = None
    channel_out: BlockingChannel | None = None
    queue_name: str | None = None
    order_number: int = 0

    def setup_connection(self) -> None:
        self.name = input("Enter supplier_name: ")

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

        items = input("Enter items in store:")

        for item in items.split(","):
            item = item.strip()
            queue_name = f"queue.{item}"
            self.channel_in.queue_declare(queue=queue_name)
            self.channel_in.queue_bind(queue=queue_name, exchange=exchange_orders, routing_key=item.strip())
            self.channel_in.basic_consume(
                queue=queue_name, on_message_callback=self.callback, auto_ack=False
            )

        self.channel_in.queue_bind(queue=self.queue_name, exchange=exchange_admin_out, routing_key="all.*")
        self.channel_in.queue_bind(queue=self.queue_name, exchange=exchange_admin_out, routing_key="supplier.*")

        print(f"Created queue: {self.queue_name}")

        print(" [*] Waiting for orders:")

    def send_order(self, crew_name: str, item: str) -> None:

        message = Message(sender=self.name, sender_type=SenderType.SUPPLIER, body=f"Order- {self.order_number}: {item}")
        self.channel_out.basic_publish(exchange=exchange_deliveries, routing_key=crew_name,
                                       body=json.dumps(message.to_dict()))
        print(f"Sent {item} to {crew_name}")
        self.send_info_to_admin(message)
        self.order_number += 1

    def send_info_to_admin(self, message: Message) -> None:
        self.channel_out.basic_publish(exchange=exchange_admin_in, routing_key="admin.supplier_info",
                                       body=json.dumps(message.to_dict()))

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        sender = data['sender']
        sender_type = data['sender_type']
        message = data['body']

        routing_key = method.routing_key

        print(f"[{routing_key}] From {sender_type}:{sender} – {message}")

        if sender_type == SenderType.CREW.name:
            self.send_order(sender, message)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def wait_for_order(self) -> None:
        self.channel_in.basic_qos(prefetch_count=1)

        self.channel_in.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=False
        )

        self.channel_in.start_consuming()


def main() -> None:
    supplier = Supplier()
    supplier.setup_connection()
    supplier.wait_for_order()


if __name__ == '__main__':
    main()

# supplier_name = input("Enter supplier_name: ")
# print(f'Register supplier: {supplier_name}')
#
# connection_in = pika.BlockingConnection(
#     pika.ConnectionParameters(host="localhost"),
# )
#
# connection_out = pika.BlockingConnection(
#     pika.ConnectionParameters(host="localhost"),
# )
#
# channel_in = connection_in.channel()
# channel_out = connection_out.channel()
#
#
#
# channel_in.exchange_declare(exchange=exchange_orders, exchange_type="topic")
# channel_in.exchange_declare(exchange=exchange_admin_out, exchange_type="topic")
# channel_out.exchange_declare(exchange=exchange_deliveries, exchange_type="topic")

# items = input("Enter items in store:")
#
# result = channel_in.queue_declare('', exclusive=True)
# queue_name = result.method.queue

# for item in items.split(","):
#     print(f'{item}')
#     channel_in.queue_bind(queue=queue_name, exchange=exchange_orders, routing_key=item.strip())
#
# channel_in.queue_bind(queue=queue_name, exchange=exchange_admin_out, routing_key="all.*")
# channel_in.queue_bind(queue=queue_name, exchange=exchange_admin_out, routing_key="supplier.*")
#
# print(f"Created queue: {queue_name}")
#
# print(" [*] Waiting for orders:")


# def send_order(crew_name: str, item: str) -> None:
#     message = Message(sender=supplier_name, sender_type=SenderType.SUPPLIER, body=item)
#     channel_out.basic_publish(exchange=exchange_deliveries, routing_key=crew_name, body=json.dumps(message.to_dict()))
#     info = f"Sent {item} to {crew_name}"
#     print(info)
#     send_info_to_admin(info=info)
#
#
# def send_info_to_admin(info: str):
#     message = Message(sender=supplier_name, sender_type=SenderType.SUPPLIER, body=info)
#     channel_out.basic_publish(exchange=exchange_admin_in, routing_key="admin.supplier_info",
#                               body=json.dumps(message.to_dict()))
#
#
# def callback(ch, method, properties, body):
#     data = json.loads(body.decode())
#     sender = data['sender']
#     sender_type = data['sender_type']
#     message = data['body']
#
#     routing_key = method.routing_key
#
#     print(f"[{routing_key}] From {sender_type}:{sender} – {message}")
#
#     if sender_type == SenderType.CREW.name:
#         send_order(sender, message)
#
#
# def wait_for_order() -> None:
#     channel_in.basic_qos(prefetch_count=1)
#
#     channel_in.basic_consume(
#         queue=queue_name, on_message_callback=callback, auto_ack=True
#     )
#
#     channel_in.start_consuming()
#
#
# wait_for_order()

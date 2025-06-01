import json
from dataclasses import dataclass
import pika
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from message import Message, SenderType, format_log
from configuration import (
    exchange_orders,
    exchange_deliveries,
    exchange_admin_in,
    exchange_admin_out,
)


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
            pika.ConnectionParameters(host="localhost", heartbeat=600),
        )

        self.connection_out = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", heartbeat=600),
        )

        self.channel_in = self.connection_in.channel()
        self.channel_out = self.connection_out.channel()

        self.channel_in.exchange_declare(
            exchange=exchange_deliveries, exchange_type="topic"
        )
        self.channel_in.exchange_declare(
            exchange=exchange_admin_out, exchange_type="topic"
        )
        self.channel_out.exchange_declare(
            exchange=exchange_orders, exchange_type="topic"
        )

        self.queue_name = f"supplier.{self.name}"
        self.channel_in.queue_declare(queue=self.queue_name)
        items = input("Enter items in store:")

        for item in items.split(","):
            item = item.strip()
            self.channel_in.queue_bind(
                queue=self.queue_name,
                exchange=exchange_orders,
                routing_key=f"order.item.{item.strip()}",
            )

        self.channel_in.queue_bind(
            queue=self.queue_name,
            exchange=exchange_admin_out,
            routing_key="broadcast.all.*",
        )
        self.channel_in.queue_bind(
            queue=self.queue_name,
            exchange=exchange_admin_out,
            routing_key="supplier.all.*",
        )
        self.channel_in.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=False
        )

        print(f"Created queue: {self.queue_name}")

        print("[*] Waiting for orders:")

    def send_order(self, crew_name: str, item: str) -> None:

        message = Message(
            sender=self.name,
            sender_type=SenderType.SUPPLIER,
            body=f"Order-{self.order_number}: {item}",
        )
        self.channel_out.basic_publish(
            exchange=exchange_deliveries,
            routing_key=f"delivery.{crew_name}",
            body=json.dumps(message.to_dict()),
        )

        print(
            format_log(
                SenderType.SUPPLIER,
                self.name,
                f"delivery.{crew_name}",
                message.body,
                direction="SENT",
            )
        )

        self.send_info_to_admin(message)
        self.order_number += 1

    def send_info_to_admin(self, message: Message) -> None:
        self.channel_out.basic_publish(
            exchange=exchange_admin_in,
            routing_key="admin.supplier.status",
            body=json.dumps(message.to_dict()),
        )

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode())
        sender = data["sender"]
        sender_type = data["sender_type"]
        message = data["body"]

        routing_key = method.routing_key

        print(
            format_log(sender_type, sender, routing_key, message, direction="RECEIVED")
        )

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


if __name__ == "__main__":
    main()

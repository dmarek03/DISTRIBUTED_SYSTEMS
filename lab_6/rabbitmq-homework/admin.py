import json
import re
import pika
from dataclasses import dataclass
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from threading import Thread
from message import Message, SenderType, format_log
from configuration import exchange_admin_in, exchange_admin_out


@dataclass
class AdminPanel:
    name: str | None = "admin"
    connection_in: BlockingConnection | None = None
    connection_out: BlockingConnection | None = None
    channel_in: BlockingChannel | None = None
    channel_out: BlockingChannel | None = None
    queue_name: str | None = None

    def setup_connection(self) -> None:
        self.connection_in = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", heartbeat=600),
        )

        self.connection_out = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost", heartbeat=600),
        )

        self.channel_in = self.connection_in.channel()
        self.channel_out = self.connection_out.channel()

        self.channel_in.exchange_declare(
            exchange=exchange_admin_in, exchange_type="topic"
        )
        self.channel_out.exchange_declare(
            exchange=exchange_admin_out, exchange_type="topic"
        )

        result = self.channel_in.queue_declare("", exclusive=True)
        self.queue_name = result.method.queue

        self.channel_in.queue_bind(
            exchange=exchange_admin_in, routing_key="admin.*.*", queue=self.queue_name
        )

    def send_broadcast(self, message: Message):
        self.channel_out.basic_publish(
            exchange=exchange_admin_out,
            routing_key="broadcast.all.info",
            body=json.dumps(message.to_dict()),
        )

        print(
            format_log(
                SenderType.ADMIN,
                "admin_panel",
                "broadcast.all.info",
                message.body,
                direction="SENT",
            )
        )

    def send_message_to_crews(self, message: Message):
        self.channel_out.basic_publish(
            exchange=exchange_admin_out,
            routing_key="crew.all.notification",
            body=json.dumps(message.to_dict()),
        )

        print(
            format_log(
                SenderType.ADMIN,
                "admin_panel",
                "crew.all.notification",
                message.body,
                direction="SENT",
            )
        )

    def send_message_to_suppliers(self, message: Message):
        self.channel_out.basic_publish(
            exchange=exchange_admin_out,
            routing_key="supplier.all.notification",
            body=json.dumps(message.to_dict()),
        )

        print(
            format_log(
                SenderType.ADMIN,
                "admin_panel",
                "supplier.all.notification",
                message.body,
                direction="SENT",
            )
        )

    @staticmethod
    def callback(ch, method, properties, body):
        data = json.loads(body.decode())
        sender = data["sender"]
        sender_type = data["sender_type"]
        message = data["body"]

        routing_key = method.routing_key

        print(
            format_log(sender_type, sender, routing_key, message, direction="RECEIVED")
        )

    def wait_for_message(self) -> None:
        self.channel_in.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=True
        )

        self.channel_in.start_consuming()

    @staticmethod
    def get_receiver(text: str) -> str:
        while not re.match(r"^[SCA]$", text := input(f"{text}")):
            pass
        return text

    def send_message(self) -> None:
        while True:
            receiver = self.get_receiver(text="Enter receiver:\n")

            message = Message(
                sender="admin_panel",
                sender_type=SenderType.ADMIN,
                body=input("Enter message:"),
            )
            match receiver:
                case "A":
                    self.send_broadcast(message)

                case "S":
                    self.send_message_to_suppliers(message)

                case "C":
                    self.send_message_to_crews(message)


def main() -> None:
    admin_panel = AdminPanel()
    admin_panel.setup_connection()
    print("Admin is waiting for messages:")
    Thread(target=admin_panel.wait_for_message, daemon=True).start()
    Thread(target=admin_panel.send_message, daemon=True).start()

    while True:
        pass


if __name__ == "__main__":
    main()

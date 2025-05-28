import re
from threading import Thread

import grpc
import sys
import time
sys.path.append("proto")

from proto.auction_house_pb2_grpc import AuctionHouseStub
from proto.auction_house_pb2 import (
    Empty,
    GetAuctionItemsRequest,
    SubscribeAuctionRequest,
    PlaceBidRequest

)

PORT = 50051
EXIT = 1

client_id = 3



def get_user_input(message: str) -> int | str:
    while not re.match(r'^[0-9]+|exit$', text := input(f'{message}:\n')):
        print(f'{text} is incorrect')
    return int(text) if text != 'exit' else text


def get_auction_ids() -> set[int]:
    auctions_ids = set()
    while (auction_id := get_user_input('Enter auction id')) != 'exit':
        auctions_ids.add(auction_id)
    return auctions_ids


def listen_for_updates(stub: AuctionHouseStub, auction_ids: list[int]):
    request = SubscribeAuctionRequest(client_id=client_id, auction_ids=auction_ids)
    try:
        for update in stub.SubscribeAuctions(request):
            print("🔔 Update received:")
            if update.HasField("updatedItem"):
                print("💸 New bid:", update.updatedItem)
            elif update.HasField("newItem"):
                print("🆕 New item:", update.newItem)
    except grpc.RpcError as err:
        print("❌ Connection lost:", err)


def execute_command(command: str, stub: AuctionHouseStub) -> int | None:

    match command:
        case "auctions":
            response = stub.GetAuctions(Empty())

            for auction in response.auctions:
                print(auction)

        case "auction items":
            auction_id = get_user_input('Enter auction id')

            request = GetAuctionItemsRequest(auction_id=auction_id)
            response = stub.GetAuctionItems(request)
            for item in response.items:
                print(item)

        case "subscribe":

            auction_ids = get_auction_ids()
            t = Thread(target=listen_for_updates, args=(stub, auction_ids), daemon=True)
            t.start()

        case "unsubscribe":
            auction_ids = get_auction_ids()

            request = SubscribeAuctionRequest(client_id=client_id, auction_ids=auction_ids)

            for status in stub.UnsubscribeAuctions(request):
                print(status)

        case 'place a bid':
            auction_id = get_user_input('Enter auction id')
            item_id = get_user_input('Enter item id')
            price = get_user_input('Enter price')

            request = PlaceBidRequest(client_id=client_id, auction_id=auction_id, item_id=item_id, price=price)

            response = stub.PlaceBid(request)

            print(response)

        case 'exit':
            print('Goodbye')
            return EXIT

        case _:
            print(f'Unknown command {command}')


def run() -> None:
    grpc_options = [
        ("grpc.keepalive_time_ms", 60000),
        ("grpc.keepalive_timeout_ms", 20000),
        ("grpc.keepalive_permit_without_calls", 0),
    ]

    socket = f'localhost:{PORT}'

    with grpc.insecure_channel(socket, options=grpc_options) as channel:
        stub = AuctionHouseStub(channel)

        while True:
            try:
                split_input = input("")
                command = split_input

                if execute_command(command, stub) == EXIT:
                    break

            except EOFError:
                print("EOF, goodbye! =)")
                break
            except Exception:
                time.sleep(1)

def main() -> None:
    run()


if __name__ == '__main__':
    main()
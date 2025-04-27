import io.grpc.Server;
import io.grpc.ServerBuilder;
import io.grpc.stub.ServerCallStreamObserver;
import io.grpc.stub.StreamObserver;
import com.google.protobuf.Timestamp;

import auction_house.AuctionHouseGrpc;
import auction_house.AuctionHouseOuterClass.*;

import java.io.IOException;
import java.text.MessageFormat;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

public class AuctionHouseServer {
    private static class AuctionHouseServiceImpl extends AuctionHouseGrpc.AuctionHouseImplBase {
        private static final AuctionType[] AUCTION_TYPES = AuctionType.values();

        private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(3);
        private final Map<Integer, Auction> auctions = new ConcurrentHashMap<>();
        private final Map<Integer, Map<Integer, AuctionItem>> itemsPerAuction = new ConcurrentHashMap<>();
        private final Map<Integer, StreamObserver<SubscriptionUpdate>> clientObservers = new ConcurrentHashMap<>();
        private final Map<Integer, Set<Integer>> clientSubscriptions = new ConcurrentHashMap<>();
        private final Map<ItemKey, Set<Integer>> itemSubscribers = new ConcurrentHashMap<>();
        private final AtomicInteger auctionIdCounter = new AtomicInteger();



        public AuctionHouseServiceImpl() {
            initializeSampleData();
            auctionIdCounter.set(auctions.keySet().stream().max(Integer::compare).orElse(-1) + 1);
            scheduleAuctionAndItemAdding();
        }


        private record ItemKey(int auctionId, int itemId) {


        }

        private void initializeSampleData() {

            Auction auction0 = createAuction(0, "Aukcja sztuki współczesnej", "Obrazy i rzeźby z XXI wieku",
                    AuctionType.STANDARD, "Krakowskie Przedmieście 15", "Warszawa", false, 7);

            Auction auction1 = createAuction(1, "Aukcja antyków", "Zabytkowe meble i przedmioty",
                    AuctionType.PREMIUM, "Wiejska 46c", "Kraków", true, 3);

            auctions.put(0, auction0);
            auctions.put(1, auction1);


            addSampleItem(0, 0, "Obraz 'Aurora'", "Olej na płótnie, 2022", 5000.0f);
            addSampleItem(0, 1, "Rzeźba 'Harmonia'", "Brąz, wys. 45 cm", 8000.0f);
            addSampleItem(1, 0, "Talar 1630", "Srebro 30g", 4000.0f);
        }

        private Auction createAuction(int id, String title, String desc, AuctionType type,
                                      String address, String city, boolean online, int days) {
            return Auction.newBuilder()
                    .setId(id)
                    .setTitle(title)
                    .setDescription(desc)
                    .setType(type)
                    .setStartTime(getCurrentTimestamp())
                    .setEndTime(getFutureTimestamp(days))
                    .setLocation(Auction.Location.newBuilder()
                            .setAddress(address)
                            .setCity(city)
                            .setOnline(online)
                            .build())
                    .build();
        }

        private void addSampleItem(int auctionId, int itemId, String name, String desc, float price) {
            AuctionItem item = AuctionItem.newBuilder()
                    .setId(itemId)
                    .setAuctionId(auctionId)
                    .setName(name)
                    .setDescription(desc)
                    .setStartPrice(price)
                    .setCurrentPrice(price)
                    .setSold(false)
                    .build();

            itemsPerAuction.computeIfAbsent(auctionId, k -> new ConcurrentHashMap<>())
                    .put(itemId, item);
        }

        @Override
        public void getAuctions(Empty request, StreamObserver<Auctions> responseObserver) {
            try {
                Auctions response = Auctions.newBuilder()
                        .addAllAuctions(auctions.values())
                        .build();
                responseObserver.onNext(response);
                responseObserver.onCompleted();
            } catch (Exception e) {
                responseObserver.onError(e);
            }
        }
        @Override
        public void getAuctionItems(GetAuctionItemsRequest request, StreamObserver<AuctionItems> responseObserver) {
            int auctionId = request.getAuctionId();


            if (!auctions.containsKey(auctionId)) {
                responseObserver.onError(new Exception("Auction with id " + auctionId + " does not exist"));
                return;
            }

            Map<Integer, AuctionItem> auctionItems = this.itemsPerAuction.get(auctionId);

            AuctionItems response = AuctionItems.newBuilder()
                    .addAllItems(auctionItems.values())
                    .build();

            responseObserver.onNext(response);
            responseObserver.onCompleted();
        }


        @Override
        public void subscribeAuctions(SubscribeAuctionRequest request, StreamObserver<SubscriptionUpdate> responseObserver) {
            int clientId = request.getClientId();


            clientObservers.put(clientId, responseObserver);


            ServerCallStreamObserver<SubscriptionUpdate> serverObserver =
                    (ServerCallStreamObserver<SubscriptionUpdate>) responseObserver;

            serverObserver.setOnCancelHandler(() -> {
                synchronized (this) {
                    clientObservers.remove(clientId);
                    clientSubscriptions.remove(clientId);
                    itemSubscribers.forEach((key, clients) -> clients.remove(clientId));
                }
                System.out.println("Client " + clientId + " disconnected");
            });


            clientSubscriptions
                    .computeIfAbsent(clientId, k -> new HashSet<>())
                    .addAll(request.getAuctionIdsList());
        }


        @Override
        public void unsubscribeAuctions(SubscribeAuctionRequest request, StreamObserver<SubscriptionStatus> responseObserver) {
            int clientId = request.getClientId();
            Set<Integer> subscriptions = clientSubscriptions.get(clientId);

            if (subscriptions == null || subscriptions.isEmpty()) {
                responseObserver.onNext(SubscriptionStatus.newBuilder()
                        .setSuccess(false)
                        .setMessage("Can not unsubscribe unsubscribed auction ")
                        .build());
                responseObserver.onCompleted();
                return;
            }

            for (int auctionId : request.getAuctionIdsList()) {
                subscriptions.remove(auctionId);
            }
            if (subscriptions.isEmpty()) {
                clientSubscriptions.remove(clientId);
            }

            itemSubscribers.forEach((key, clients) -> clients.remove(clientId));




            responseObserver.onNext(SubscriptionStatus.newBuilder()
                    .setSuccess(true)
                    .setMessage("Successfully cancelled subscription for auctions: " + request.getAuctionIdsList())
                    .build());
            responseObserver.onCompleted();
        }

        @Override
        public void placeBid(PlaceBidRequest request, StreamObserver<BidStatus> responseObserver) {
            int clientId = request.getClientId();
            int itemId = (int) request.getItemId();
            int auctionId = request.getAuctionId();

            if (!auctions.containsKey(auctionId) || !itemsPerAuction.containsKey(auctionId)) {
                responseObserver.onNext(BidStatus.newBuilder()
                        .setSuccess(false)
                        .setMessage("Auction does not exit or items not found")
                        .build());
                responseObserver.onCompleted();
                return;
            }


            Map<Integer, AuctionItem> auctionItems = this.itemsPerAuction.get(auctionId);
            AuctionItem item = auctionItems.get(itemId);

            if (item == null) {
                responseObserver.onNext(BidStatus.newBuilder()
                        .setSuccess(false)
                        .setMessage("Item not found")
                        .build());
                responseObserver.onCompleted();
                return;
            }

            synchronized (this) {
                if (request.getPrice() <= item.getCurrentPrice()) {
                    responseObserver.onNext(BidStatus.newBuilder()
                            .setSuccess(false)
                            .setNewPrice(item.getCurrentPrice())
                            .setMessage("Offer must be greater than " + item.getCurrentPrice())
                            .build());
                } else {

                    AuctionItem updatedItem = item.toBuilder()
                            .setCurrentPrice(request.getPrice())
                            .build();
                    auctionItems.put(itemId, updatedItem);

                    responseObserver.onNext(BidStatus.newBuilder()
                            .setSuccess(true)
                            .setNewPrice(request.getPrice())
                            .setMessage("Offer accepted")
                            .build());

                    ItemKey key = new ItemKey(itemId, auctionId);
                    itemSubscribers.computeIfAbsent(key, k ->ConcurrentHashMap.newKeySet()).add(clientId);

                    notifySubscribersAboutBidOrNewItem(updatedItem, false);
                }
                responseObserver.onCompleted();
            }
        }





        private void notifySubscribersAboutBidOrNewItem(AuctionItem item, boolean isNewItem) {
            int auctionId = item.getAuctionId();
            SubscriptionUpdate update = createUpdate(item, isNewItem);

            if (isNewItem) {

                notifyAuctionSubscribers(auctionId, update);
            } else {

                notifyItemBidders(item, update);
            }
        }




        private void notifyAuctionSubscribers(int auctionId, SubscriptionUpdate update) {
            clientSubscriptions.forEach((clientId, subscribedAuctions) -> {
                if(subscribedAuctions.contains(auctionId)) {
                    sendUpdate(clientId, update);
                }
            });
        }

        private void notifyItemBidders(AuctionItem item,SubscriptionUpdate update) {
            ItemKey key = new ItemKey(item.getAuctionId(), item.getId());
            Set<Integer> bidders = itemSubscribers.getOrDefault(key, Collections.emptySet());


            bidders.forEach(clientId -> sendUpdate(clientId, update));
        }

        private void sendUpdate(int clientId, SubscriptionUpdate update) {
            StreamObserver<SubscriptionUpdate> observer = clientObservers.get(clientId);

            if(observer != null) {
                try{
                    observer.onNext(update);

                }catch (Exception e) {
                    System.out.println("Error during sending to client " + clientId);
                }
            }
        }

        private void createNewAuction() {
            try {
                int auctionId = auctionIdCounter.getAndIncrement();
                ThreadLocalRandom rand = ThreadLocalRandom.current();

                Auction newAuction = Auction.newBuilder()
                        .setId(auctionId)
                        .setTitle("New auction " + auctionId)
                        .setDescription("Description of new auction " + auctionId)
                        .setType(AUCTION_TYPES[rand.nextInt(AUCTION_TYPES.length-1)])
                        .setStartTime(getCurrentTimestamp())
                        .setEndTime(getFutureTimestamp(rand.nextInt(30)))
                        .setLocation(Auction.Location.newBuilder()
                                .setAddress("Address of new auction " + auctionId)
                                .setCity("City of new auction " + auctionId)
                                .setOnline(rand.nextBoolean())
                                .build())
                        .build();

                auctions.put(auctionId, newAuction);
                itemsPerAuction.put(auctionId, new ConcurrentHashMap<>());
                System.out.println("Added new auction " + auctionId);
            } catch (Exception e) {
                System.err.println("Error creating auction: " + e.getMessage());
            }
        }

        private SubscriptionUpdate createUpdate(AuctionItem item, boolean isNewItem){
            return isNewItem
                    ? SubscriptionUpdate.newBuilder()
                    .setAuctionId(item.getAuctionId())
                    .setNewItem(item)
                    .build()
                    : SubscriptionUpdate.newBuilder()
                    .setAuctionId(item.getAuctionId())
                    .setUpdatedItem(item)
                    .build();
        }

        private void createNewItem() {
            try {
                ThreadLocalRandom rand = ThreadLocalRandom.current();
                List<Integer> auctionIds = new ArrayList<>(auctions.keySet());
                if (auctionIds.isEmpty()) return;

                int auctionId = auctionIds.get(rand.nextInt(auctionIds.size()));
                Map<Integer, AuctionItem> items = itemsPerAuction.get(auctionId);

                int itemId = items.values().stream()
                        .mapToInt(AuctionItem::getId)
                        .max()
                        .orElse(-1) + 1;

                float startPrice = Math.round(rand.nextFloat() * 10000 * 100) / 100.0f;
                float currentPrice = Math.round((startPrice + rand.nextFloat() * 0.2f * startPrice) * 100) / 100.0f;

                AuctionItem newItem = AuctionItem.newBuilder()
                        .setId(itemId)
                        .setAuctionId(auctionId)
                        .setName("New item " + itemId)
                        .setDescription("Description of new item " + itemId)
                        .setStartPrice(startPrice)
                        .setCurrentPrice(currentPrice)
                        .setSold(false)
                        .build();

                items.put(itemId, newItem);
                notifySubscribersAboutBidOrNewItem(newItem, true);
                System.out.println(MessageFormat.format("Added new item {0} to auction {1}", itemId, auctionId));
            } catch (Exception e) {
                System.err.println("Error creating item: " + e.getMessage());
            }
        }

        private void placeRandomBid() {
            try {
                ThreadLocalRandom rand = ThreadLocalRandom.current();
                List<Integer> auctionIds = new ArrayList<>(auctions.keySet());
                if (auctionIds.isEmpty()) return;

                int auctionId = auctionIds.get(rand.nextInt(auctionIds.size()));
                Map<Integer, AuctionItem> items = itemsPerAuction.get(auctionId);

                if (items == null || items.isEmpty()) {
                    System.out.println("No items in auction " + auctionId);
                    return;
                }

                List<Integer> itemIds = new ArrayList<>(items.keySet());
                int itemId = itemIds.get(rand.nextInt(itemIds.size()));
                AuctionItem item = items.get(itemId);

                float newPrice = item.getCurrentPrice() + rand.nextFloat() * 0.1f * item.getCurrentPrice();
                AuctionItem updatedItem = item.toBuilder().setCurrentPrice(newPrice).build();

                items.put(itemId, updatedItem);
                notifySubscribersAboutBidOrNewItem(updatedItem, false);
                System.out.println(MessageFormat.format("Placed bid on item {0} from auction {1} ", itemId, auctionId));
            } catch (Exception e) {
                System.err.println("Error placing bid: " + e.getMessage());
            }
        }

        private Timestamp getCurrentTimestamp() {
            Instant now = Instant.now();
            return Timestamp.newBuilder()
                    .setSeconds(now.getEpochSecond())
                    .setNanos(now.getNano())
                    .build();
        }

        private Timestamp getFutureTimestamp(int days) {
            Instant future = Instant.now().plusSeconds((long) days * 24 * 60 * 60);
            return Timestamp.newBuilder()
                    .setSeconds(future.getEpochSecond())
                    .setNanos(future.getNano())
                    .build();
        }


        private void scheduleAuctionAndItemAdding() {
            scheduler.scheduleAtFixedRate(() -> {
                try {
                    createNewAuction();
                } catch (Exception e) {
                    System.err.println("Scheduler error in createNewAuction: " + e.getMessage());
                }
            }, 1, 30, TimeUnit.SECONDS);

            scheduler.scheduleAtFixedRate(() -> {
                try {
                    createNewItem();
                } catch (Exception e) {
                    System.err.println("Scheduler error in createNewItem: " + e.getMessage());
                }
            }, 1, 15, TimeUnit.SECONDS);

            scheduler.scheduleAtFixedRate(() -> {
                try {
                    placeRandomBid();
                } catch (Exception e) {
                    System.err.println("Scheduler error in placeRandomBid: " + e.getMessage());
                }
            }, 1, 5, TimeUnit.SECONDS);
        }


    }


    public static void main(String[] args) throws IOException, InterruptedException {
        int port = 50051;
        Server server = ServerBuilder.forPort(port)
                .addService(new AuctionHouseServiceImpl())
                .build()
                .start();

        System.out.println("Server running on port " + port);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down server...");
            server.shutdown();
        }));
        server.awaitTermination();
    }
}
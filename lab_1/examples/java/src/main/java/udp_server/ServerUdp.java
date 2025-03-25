package udp_server;
import java.io.IOException;
import java.net.*;



public class ServerUdp {

    final static int port = 9000;



    public static void main(String[] args) throws IOException{

        DatagramSocket serverSocket = new DatagramSocket(port);
        System.out.println("Udp server listening on port:" + port);

        while (true){

            try {
                byte[] buffer = new byte[1024];
                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                serverSocket.receive(receivePacket);
                String receivedMessage = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("Received from client: " + receivedMessage);

                int clientPort = receivePacket.getPort();
                InetAddress clientAddress  = receivePacket.getAddress();
                if (receivedMessage.equals("exit")){
                    buffer = "exit".getBytes();

                }

                DatagramPacket sendPacket = new DatagramPacket(buffer, buffer.length, clientAddress, clientPort);
                serverSocket.send(sendPacket);


            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }

    }
}

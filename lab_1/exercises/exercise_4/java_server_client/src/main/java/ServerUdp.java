import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;


public class ServerUdp {



    private static final int port = 9010;




    public static void main(String[] args) {
       ;
        byte[] buffer = new byte[1024];
        byte[] responseBuffer ;

        try (DatagramSocket socket = new DatagramSocket(port)) {
            while (true) {
                DatagramPacket receivedPacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(receivedPacket);
                String receivedMessage = new String(receivedPacket.getData(), 0, receivedPacket.getLength());
                System.out.println("Received from client: " + receivedMessage);


                int clientPort = receivedPacket.getPort();
                InetAddress clientAddress = receivedPacket.getAddress();


                String response = "PONG UNKNOWN";
                if (receivedMessage.startsWith("JAVA")) {
                    response = "PONG JAVA";
                }

                if (receivedMessage.startsWith("PYTHON")) {
                    response = "PONG PYTHON";
                }

                if (receivedMessage.endsWith("exit")){
                    response = "EXIT";
                }

                responseBuffer = response.getBytes();

                DatagramPacket sendPacket = new DatagramPacket(responseBuffer, responseBuffer.length, clientAddress, clientPort);
                socket.send(sendPacket);
            }

        } catch (Exception e) {
            throw new RuntimeException(e);
        }

    }
}

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;


public class ServerUdp {



    private static final int port = 9008;




    public static void main(String[] args)  {


        try (DatagramSocket socket = new DatagramSocket(port)){
            byte[] buffer = new byte[4];

            while (true) {
                DatagramPacket receivedPacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(receivedPacket);

                int receivedNumber = ByteBuffer.wrap(receivedPacket.getData()).order(ByteOrder.LITTLE_ENDIAN).getInt();
                System.out.println("Received from client: " + receivedNumber);

                int clientPort = receivedPacket.getPort();
                InetAddress clientAddress = receivedPacket.getAddress();
                buffer = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(receivedNumber + 1).array();
                DatagramPacket sendPacket = new DatagramPacket(buffer, buffer.length, clientAddress, clientPort);
                socket.send(sendPacket);




            }

        } catch (IOException e) {
            throw new RuntimeException(e);
        }

    }
}

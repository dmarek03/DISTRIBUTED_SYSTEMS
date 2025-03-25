import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.util.Scanner;

public class ClientUdp {
    private final static int port = 9010;



    public static void main(String[] args) {


        try (DatagramSocket socket = new DatagramSocket()) {

            InetAddress serverAddress = InetAddress.getLocalHost();
            System.out.println("Server Address: " + serverAddress);
            byte[] buffer;
            System.out.println("Client Udp");
            Scanner in = new Scanner(System.in);

            while (true) {
                System.out.println("Send message to server:");
                String message = in.nextLine();
                String message_from_java = "JAVA| " + message;
                buffer = message_from_java.getBytes();
                DatagramPacket sendPacket = new DatagramPacket(buffer, buffer.length, serverAddress, port);
                socket.send(sendPacket);

                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(receivePacket);
                String receivedMessage = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("Received from server:" + receivedMessage);

                if (receivedMessage.equals("EXIT")) {
                    socket.close();
                    break;
                }
            }


        } catch (IOException e) {
            throw new RuntimeException(e);
        }


    }
}

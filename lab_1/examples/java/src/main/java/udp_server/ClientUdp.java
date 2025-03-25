package udp_server;

import java.io.IOException;
import java.net.*;
import java.util.Scanner;

public class ClientUdp {
    final static int port = 9000;



    public static void main(String[] args) throws IOException  {
        DatagramSocket socket = new DatagramSocket();
        InetAddress address = InetAddress.getByName("localhost");
        Scanner sc = new Scanner(System.in);
        System.out.println("UDP Client");
        byte[] buffer ;
        while (true){
            try {
                System.out.println("Send message to sever:");
                String message = sc.nextLine();
                buffer = message.getBytes();
                DatagramPacket SendPacket = new DatagramPacket(buffer, buffer.length, address, port);
                socket.send(SendPacket);

                DatagramPacket receivePacket = new DatagramPacket(buffer, buffer.length);
                socket.receive(receivePacket);
                String receivedMessage = new String(receivePacket.getData(), 0, receivePacket.getLength());
                System.out.println("Received from server:" + receivedMessage);

                if (receivedMessage.equals("exit")){
                    System.out.println("Exiting server ");
                    socket.close();
                    break;
                }
            } catch (IOException e) {
                throw new RuntimeException(e);
            }


        }
    }
}



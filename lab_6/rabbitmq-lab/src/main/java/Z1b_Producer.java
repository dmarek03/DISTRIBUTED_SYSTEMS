import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Z1b_Producer {

    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 PRODUCER");

        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1b";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);

        // producer (publish msg)
        for (int i = 0; i < 10; i++) {
            String msg = br.readLine(); // użytkownik wpisuje 1 lub 5
            channel.basicPublish("", QUEUE_NAME, null, msg.getBytes());
            System.out.println("Sent: " + msg);
        }



        // close
        channel.close();
        connection.close();
    }
}

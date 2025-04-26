import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.ObjectPrx;
import com.zeroc.Ice.Properties;
import com.zeroc.Ice.Util;
import TestSystem.StudentTestPrx;
import java.util.Scanner;

public class Client {

    private static Communicator communicator;
    private static String endpoints;
    private static final String studentId = "student2";

    public static void main(String[] args) {
        communicator = Util.initialize(args, "config.client");
        Properties props = communicator.getProperties();
        endpoints = props.getProperty("TestSystem.endpoints");

        System.out.println("Using endpoints: " + endpoints);

        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.print(">> ");
            String input = scanner.nextLine().trim();
            if (input.isEmpty()) continue;

            String[] parts = input.split(" ");
            String command = parts[0];

            try {
                switch (command) {
                    case "start":
                        System.out.println("Enter question number:");
                        int limit = Integer.parseInt(scanner.nextLine());
                        startTest(limit);
                        break;
                    case "answer":
                        System.out.print("Enter question id: ");
                        int questionId = Integer.parseInt(scanner.nextLine());
                        System.out.print("Enter answer: ");
                        String answer = scanner.nextLine();
                        answerQuestion(questionId, answer);
                        break;
                    case "finish":
                        finishTest();
                        break;
                    case "exit":
                        communicator.destroy();
                        System.exit(0);
                        break;
                    default:
                        System.out.println("Unknown command!");
                }
            } catch (Exception e) {
                System.out.println("Error: " + e.getMessage());
            }
        }
    }

    private static StudentTestPrx getStudentTestProxy() {
        ObjectPrx base = communicator.stringToProxy("student_test/" + studentId + ":" + endpoints);
        return StudentTestPrx.checkedCast(base);
    }

    private static void startTest(int limit) {
        StudentTestPrx studentTest = getStudentTestProxy();
        if (studentTest != null) {
            String[] questions = studentTest.startTest(limit);
            for(int i =0 ; i < questions.length ; i++) {
                System.out.println("Question " + i + ": " + questions[i]);
            }
            System.out.println("Test started.");
        } else {
            System.out.println("Could not find test proxy!");
        }
    }

    private static void answerQuestion(int questionId, String answer) {
        StudentTestPrx studentTest = getStudentTestProxy();
        if (studentTest != null) {
            studentTest.answerQuestion(questionId, answer);
            System.out.println("Answer submitted.");
        } else {
            System.out.println("Could not find test proxy!");
        }
    }

    private static void finishTest() {
        StudentTestPrx studentTest = getStudentTestProxy();
        if (studentTest != null) {
            double result = studentTest.finishTest();
            System.out.println("Final score: " + result + "%");
        } else {
            System.out.println("Could not find test proxy!");
        }
    }
}

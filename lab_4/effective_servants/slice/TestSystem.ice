module TestSystem {
    sequence<string> QuestionList;
    interface StudentTest{
        QuestionList startTest(int limit);
        void answerQuestion(int questionId, string answer);
        float finishTest();
    };

    interface TestEvaluator{
        QuestionList getTestQuestions(int limit);
        string getQuestion(int questionId);
        string getAnswer(int questionId);
    };


};
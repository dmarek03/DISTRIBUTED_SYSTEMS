import json
import os.path
import sys
from collections import defaultdict, OrderedDict
from typing import Union

import Ice
Ice.loadSlice('../slice/TestSystem.ice')
import TestSystem


class StudentTestI(TestSystem.StudentTest):
    def __init__(self, name, evaluator_proxy, restored_answers=None):
        self.name = name
        self.answers = defaultdict(str, restored_answers or {})
        self.evaluator = TestSystem.TestEvaluatorPrx.checkedCast(evaluator_proxy)
        print(f"Test for student: {name} created, restored: {bool(restored_answers)}")

    def save_stat(self) -> None:
        path = f'state_{self.name}.json'

        with open(path, "w", encoding='utf-8') as f:
            json.dump(self.answers, f)

        print(f"State save do {path}")

    @staticmethod
    def load_state(name):

        def int_keys_object_hook(d):
            return {int(k): v for k, v in d.items()}

        path = f"state_{name}.json"

        if os.path.exists(path):
            with open(path, 'r', encoding="utf-8") as f:
                data = json.load(f, object_hook=int_keys_object_hook)
                print(f'State loaded from {path}')
                return data

        return None

    def startTest(self, limit, current=None):
        print("Starting Test")
        return self.evaluator.getTestQuestions(limit=limit)

    def answerQuestion(self, questionId, answer, current=None):
        self.answers[questionId] = answer
        print(f'Student: {self.name} answer: {answer} for question: {questionId} was saved')

    def finishTest(self, current=None) -> float:
        score = 0
        total_points = len(self.answers)

        for question_id, answer in self.answers.items():
            correct_answer = self.evaluator.getAnswer(question_id)
            if correct_answer == answer:
                score += 1

        result = 100 * score // total_points
        print(f"Student:{self.name} achieved {result}%")
        return result


class StudentTestLocator(Ice.ServantLocator):

    def __init__(self, evaluator_proxy, max_count):
        self.servants: OrderedDict[str, StudentTestI] = OrderedDict()
        self.evaluator = evaluator_proxy
        self.max_count = max_count
        print("StudentTestLocator with LRU evictor created")

    def locate(self, current):

        student_id = current.id.name
        print(f"Locating servant for: {student_id}")

        if student_id in self.servants:
            servant = self.servants.pop(student_id)
            self.servants[student_id] = servant
            return servant

        if len(self.servants) >= self.max_count:
            old_id, old_servant = self.servants.popitem(last=False)

            print(f'Evicting LRU servant: {old_id}')

            old_servant.save_stat()

        restored = StudentTestI.load_state(student_id)

        servant = StudentTestI(student_id, self.evaluator, restored)

        self.servants[student_id] = servant
        return servant

    def finished(self, current, servant, cookie):
        print("StudentTestLocator finished")
        pass

    def deactivate(self, category):
        print("StudentTestLocator deactivated")
        pass


class TestEvaluatorI(TestSystem.TestEvaluator):

    def __init__(self):
        self.question_list = {0: "2+2=?", 1: "3*3+1=?", 2: "When WWII started?"}
        self.answers_list = {0: "4", 1: "10", 2: "01.09.1939"}
        print("Test Evaluator created")

    def getQuestion(self, questionId, current=None):
        if questionId not in self.question_list:
            print(f"Question with id: {questionId} not found")
            return
        print(f"Test Evaluator - getting question with id: {questionId}")
        return self.question_list[questionId]

    def getAnswer(self, questionId, current=None):
        if questionId not in self.question_list:
            print(f"Question with id: {questionId} not found")
            return
        return self.answers_list[questionId]

    def getTestQuestions(self, limit, current=None):
        return list(self.question_list.values())[:limit]


def main() -> None:
    with Ice.initialize(sys.argv, "./config.server") as communicator:
        adapter = communicator.createObjectAdapter("TestSystemAdapter")
        test_evaluator_proxy = adapter.add(TestEvaluatorI(), Ice.stringToIdentity("test_evaluator"))
        adapter.addServantLocator(StudentTestLocator(evaluator_proxy=test_evaluator_proxy, max_count=1), "student_test")

        adapter.activate()
        communicator.waitForShutdown()


if __name__ == '__main__':
    main()

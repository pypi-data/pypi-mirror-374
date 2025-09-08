from enum import Enum
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry

class AnswerStatus(Enum):
    OK = "AnswerStatus_OK"
    ERROR = "AnswerStatus_ERROR"

class Answer:
    def __init__(self, *, inquiry: Inquiry, answer: str, status: AnswerStatus = AnswerStatus.OK):
        self.inquiry = inquiry
        self.member = None
        self.answer = answer
        self.status = status

    def set_answer(self, answer):
        self.answer = answer

    def set_member(self, member):
        self.member = member

    def set_status(self, status: AnswerStatus):
        self.status = status
        
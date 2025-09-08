from abc import ABC, abstractmethod

from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag


class EnsembleMember(ABC):

    def __init__(self, *, config:ReasonerConfig|None=None):
        self.config = config

    @classmethod
    @abstractmethod
    def get_task_tag(cls) -> TaskTag:
        pass

    @abstractmethod
    def handle_inquiry(self, inquiry: Inquiry) -> Answer:
        pass

from abc import abstractmethod
from enum import Enum
from typing import Generator
from llama_cpp import CreateCompletionResponse, LogitsProcessorList, Llama
from transformers.models.auto.tokenization_auto import PreTrainedTokenizerFast
from vital_llm_reasoner.reasoner.ensemble_prompt import EnsemblePrompt


class EnsembleReasonerType(Enum):

    QWQ_REASONER = "QWQ_REASONER"
    R1_REASONER = "R1_REASONER"
    OSS_REASONER = "OSS_REASONER"


class EnsembleReasoner:

    @abstractmethod
    def generate_tokens(self, prompt: EnsemblePrompt, logits_processor: LogitsProcessorList) -> Generator[CreateCompletionResponse, None, None]:
        pass

    @abstractmethod
    def get_tokenizer(self) -> PreTrainedTokenizerFast:
        pass

    @abstractmethod
    def get_llm(self) -> Llama:
        pass

    @abstractmethod
    def get_reasoner_type(self) -> EnsembleReasonerType:
        pass
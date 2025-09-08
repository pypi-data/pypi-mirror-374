from typing import Generator
from llama_cpp import Llama, LogitsProcessor, CreateCompletionResponse, LogitsProcessorList
from transformers import AutoTokenizer
from transformers.models.auto.tokenization_auto import PreTrainedTokenizerFast

from vital_llm_reasoner.reasoner.ensemble_prompt import EnsemblePrompt
from vital_llm_reasoner.reasoner.ensemble_reasoner import EnsembleReasoner, EnsembleReasonerType


class OSSReasoner(EnsembleReasoner):

    def __init__(self, *, tokenizer_path: str, model_path: str, **kwargs):
        super().__init__(**kwargs)
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.reasoner_type = EnsembleReasonerType.OSS_REASONER

        # Harmony-capable tokenizer (o200k_harmony superset)
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            use_fast=True,
            add_prefix_space=True,
            trust_remote_code=True
        )

        # Ensure padding is defined; pad_token is typically <|endoftext|> for OSS
        if self.tokenizer.pad_token is None:
            # Fallback to eos if pad is not set (eos is <|return|> in OSS config)
            if getattr(self.tokenizer, "eos_token", None) is not None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"

        # Initialize the model
        self.llm = Llama(
            logits_all=True,
            model_path=self.model_path,
            n_ctx=32768,
            n_batch=512,
            n_gpu_layers=1000,
            verbose=True,
            use_mlock=True,
            use_mmap=True,
            n_threads=4,
        )

    def get_tokenizer(self) -> PreTrainedTokenizerFast:
        return self.tokenizer

    def get_llm(self) -> Llama:
        return self.llm

    def get_reasoner_type(self) -> EnsembleReasonerType:
        return self.reasoner_type

    def generate_tokens(
        self,
        prompt: EnsemblePrompt,
        logits_processor: LogitsProcessorList
    ) -> Generator[CreateCompletionResponse, None, None]:

        sampling_params = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 200,
        }

        # Use the HF chat template which renders Harmony format for OSS models
        # Example: <|start|>user<|message|>...<|end|> <|start|>assistant
        prompt_text = self.tokenizer.apply_chat_template(
            prompt.prompt,
            tokenize=False,
            add_generation_prompt=True
        )

        print("----prompt----")
        print(prompt_text)
        print("----end-prompt----")

        # Harmony guidance: stop on <|return|> (final) or <|call|> (tool request).
        # Also include <|endoftext|> as a safety stop.
        for token_data in self.llm(
            prompt_text,
            logits_processor=logits_processor,
            max_tokens=8000,
            stop=[
                "<|return|>",
                "<|call|>",
                "<|endoftext|>",
            ],
            echo=True,     # Keep consistent with other reasoners
            stream=True,   # Enable streaming
            **sampling_params
        ):
            yield token_data
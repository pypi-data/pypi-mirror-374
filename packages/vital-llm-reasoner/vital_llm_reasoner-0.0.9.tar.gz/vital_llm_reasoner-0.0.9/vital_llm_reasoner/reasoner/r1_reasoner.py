from typing import Generator
from llama_cpp import Llama, LogitsProcessor, CreateCompletionResponse, LogitsProcessorList
from transformers import AutoTokenizer
from transformers.models.auto.tokenization_auto import PreTrainedTokenizerFast

from vital_llm_reasoner.reasoner.ensemble_prompt import EnsemblePrompt
from vital_llm_reasoner.reasoner.ensemble_reasoner import EnsembleReasoner, EnsembleReasonerType


class R1Reasoner(EnsembleReasoner):

    # the initial <think> token is getting chopped somewhere

    def __init__(self, *, tokenizer_path: str, model_path: str, **kwargs):
        super().__init__(**kwargs)
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.reasoner_type = EnsembleReasonerType.R1_REASONER

        # this path doesn't work
        # self.tokenizer = PreTrainedTokenizerFast.from_pretrained(tokenizer_path)

        self.tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Llama-70B")

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = 'left'


        # Initialize the model with Metal GPU acceleration
        self.llm = Llama(
            # preserve_whitespace=True, # is this a real param?
            logits_all=True,
            model_path=self.model_path,
            n_ctx=32768,  # Matching your Ollama config
            n_batch=512,  # Batch size for prompt processing
            n_gpu_layers=1000,  # Load as many layers as possible to GPU
            verbose=True,  # Enable verbose output
            use_mlock=True,  # Pin memory to prevent swapping
            use_mmap=True,  # Use memory mapping
            n_threads=4,  # Minimal CPU threads since we're using GPU
        )

    def get_tokenizer(self) -> PreTrainedTokenizerFast:
        return self.tokenizer

    def get_llm(self) -> Llama:
        return self.llm

    def get_reasoner_type(self) -> EnsembleReasonerType:
        return self.reasoner_type

    def generate_tokens(self, prompt: EnsemblePrompt, logits_processor: LogitsProcessorList) -> Generator[
        CreateCompletionResponse, None, None]:

        sampling_params = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 200,
        }

        # print(self.tokenizer.special_tokens_map)

        prompt_text = self.tokenizer.apply_chat_template(
            prompt.prompt,
            tokenize=False,
            add_generation_prompt=False)

        # get warning if this is duplicated
        prompt_text = prompt_text.replace("<｜begin▁of▁sentence｜>", "")

        prompt_text = prompt_text + "\n<|Assistant|>: "

        print("----prompt----")
        print(prompt_text)
        print("----end-prompt----")

        for token_data in self.llm(
                prompt_text,
                logits_processor=logits_processor,
                max_tokens=8000,
                stop=[
                    "<|end▁of▁sentence|>",  # Llama 3.3 likely uses this
                    "<|User|>",  # Adjust based on chat_template format
                    # "<|Assistant|>",  # Ensure it matches metadata tokens
                ],
                echo=True, # ??
                stream=True,  # Enable streaming

                **sampling_params
        ):
            yield token_data


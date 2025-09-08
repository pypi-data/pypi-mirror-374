from llama_cpp import LogitsProcessor, Llama

from vital_llm_reasoner.config.reasoner_config import ReasonerConfig


class LogitsDefaultProcessor(LogitsProcessor):
    def __init__(self, orchestrator, llm: Llama, tokenizer, *, config: ReasonerConfig = None):
        from vital_llm_reasoner.ensemble.process.orchestrator import Orchestrator
        assert isinstance(orchestrator, Orchestrator)

        self.orchestrator = orchestrator
        self.llm = llm
        self.tokenizer = tokenizer  # Pass the tokenizer to decode tokens
        self.gen_buffer = ""
        self.result_count = 0
        self.config = config
        self.ensemble_result = None
        self.ensemble_result_tokens = None

    def __call__(self, input_ids, scores):
        return scores


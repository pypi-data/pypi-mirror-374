import logging
from llama_cpp import Llama
import os
import json
import time
import re
from tqdm import tqdm
import numpy as np
import torch
import string
from typing import Optional, Tuple, List, Dict
import argparse
from transformers import LogitsProcessor, LogitsProcessorList
from transformers import AutoTokenizer
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from pyergo import \
    pyergo_start_session, pyergo_end_session,       \
    pyergo_command, pyergo_query

# Define special tokens
BEGIN_SEARCH_QUERY = "<|begin_search_query|>"
END_SEARCH_QUERY = "<|end_search_query|>"
BEGIN_SEARCH_RESULT = "<|begin_search_result|>"
END_SEARCH_RESULT = "<|end_search_result|>"

search_result = "Jimmy Carter's birthday is: October 1, 1924"


class PrintLogitsAndTokenProcessor(LogitsProcessor):
    def __init__(self, llm: Llama, tokenizer):
        self.llm = llm
        self.tokenizer = tokenizer  # Pass the tokenizer to decode tokens
        self.gen_buffer = ""
        self.result_count = 0

    def __call__(self, input_ids, scores):
        # Decode the current token from input_ids
        if input_ids.size > 0:
            current_token = self.tokenizer.decode([input_ids[-1]])
        else:
            current_token = "" # "<No input IDs yet>"

        # Print the token and its logits
        # print(f"\nCurrent Token: {current_token}")
        # print("Logits for the current token:")
        # print(scores[:10])  # Print only the first 10 logits for readability

        # save state at beginning of search


        self.gen_buffer += current_token

        if END_SEARCH_QUERY in self.gen_buffer:
            # print("\n\nLOGITS: END_SEARCH_QUERY detected. Stopping generation.")
            # revert to the saved state and insert the search results from here

            tokens = self.tokenizer.encode(search_result)

            if self.result_count < len(tokens):

                saved_state = self.llm.save_state()

                state_size = saved_state.llama_state_size

                print(f"Saved state size: { state_size / (1024 * 1024):.2f} MB")

                # self.llm.load_state(self.saved_state)

                saved_state = None

                scores[:] = -float('inf')  # Mask all tokens

                token_id = tokens[self.result_count] # self.tokenizer.encode(tokens[self.result_count])[0]

                scores[token_id] = float('inf')
                self.result_count += 1

        # probabilities = np.exp(scores - np.max(scores))  # Stabilized softmax
        # probabilities /= np.sum(probabilities)
        # print("Probabilities:", probabilities)

        return scores  # Return the unmodified logits



from bing_search import (
    bing_web_search,
    extract_relevant_info,
    fetch_page_content,
    extract_snippet_with_context
)

from prompts import (
    get_gpqa_search_o1_instruction,
    get_math_search_o1_instruction,
    get_code_search_o1_instruction,
    get_singleqa_search_o1_instruction,
    get_multiqa_search_o1_instruction,
    get_webpage_to_reasonchain_instruction,
    get_task_instruction_openqa,
    get_task_instruction_math,
    get_task_instruction_multi_choice,
    get_task_instruction_code,
)



def create_prompt(system_message, user_message):
    """Create a prompt using the same template as Ollama Modelfile"""
    return f"""<|system|>
{system_message}
<|endoftext|>
<|user|>
{user_message}
<|endoftext|>
<|assistant|>
"""


def main():
    logging.basicConfig(level=logging.INFO)

    MAX_SEARCH_LIMIT = 5
    MAX_TURN = 15

    config_file_path = "../reasoner_config.yaml"
    reasoner_config = ReasonerConfig(config_file_path)

    # Log the loaded configuration
    logging.info("Configuration Loaded:")

    bing_subscription_key = reasoner_config.bing_subscription_key
    bing_endpoint = reasoner_config.bing_endpoint
    use_jina = reasoner_config.use_jina
    jina_api_key = reasoner_config.bing_endpoint

    ergo_root = reasoner_config.ERGO_ROOT
    xsb_dir = reasoner_config.XSB_DIR

    pyergo_start_session(xsb_dir, ergo_root)
    pyergo_command("writeln('Hello World!')@\\plg.")
    pyergo_command("add {'/Users/hadfield/Local/vital-git/vital-logic-python/test_rules/test_rules.ergo' >> logic}.")
    for row in pyergo_query('?C::Thing@logic, Socrates:?C@logic.'):
        # print("row", row[0])
        [(XVarname, XVarVal)] = row[0]
        # Xresult = XVarname + '=' + str(XVarVal)
        class_result = str(XVarVal)[1:-1]
        # print("result: ", Xresult, row[1], row[2], row[3].value)
        print("Socrates classification: " + class_result)
    for row in pyergo_query('?C::Thing@logic, Merlin:?C@logic.'):
        # print("row", row[0])
        [(XVarname, XVarVal)] = row[0]
        class_result = str(XVarVal)[1:-1]
        print("Merlin classification: " + class_result)
    pyergo_end_session()

    # Initialize model path

    model_path = "/Users/hadfield/models/QwQ-32B-Preview-Q5_K_S.gguf"

    # Check if model exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    print("\nInitializing model with Metal GPU acceleration...")

    tokenizer = AutoTokenizer.from_pretrained("/Users/hadfield/models/", trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'left'

    # Initialize the model with Metal GPU acceleration
    llm = Llama(
        logits_all=True,
        model_path=model_path,
        n_ctx=32768,  # Matching your Ollama config
        n_batch=512,  # Batch size for prompt processing
        n_gpu_layers=1000,  # Load as many layers as possible to GPU
        verbose=True,  # Enable verbose output
        use_mlock=True,  # Pin memory to prevent swapping
        use_mmap=True,  # Use memory mapping
        n_threads=4,  # Minimal CPU threads since we're using GPU
    )


    # System message and user prompt
    # system_message = "You are a reasoning assistant.  You think step by step. You carefully consider your responses. Once you come up with an answer, you re-think it one more time." # "You are a reasoning knowledgeable assistant specializing in providing accurate information on a wide range of topics."
    system_message = "You are a reasoning assistant.  You are thorough and accurate."

    # user_message = "how many s's are in Mississippi?"

    # user_message = "how many vowels are in this exact sentence?"

    user_message = "What is Jimmy Carter's birthday?"

    # Create formatted prompt
    # prompt = create_prompt(system_message, user_message)

    instruction = get_singleqa_search_o1_instruction(MAX_SEARCH_LIMIT)

    user_prompt = get_task_instruction_openqa(user_message)

    prompt = [{"role": "user", "content": instruction + user_prompt}]
    prompt = tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)

    logging.info("\nModel loaded successfully. Running inference...")

    sampling_params = {
        "temperature": 0.7,  # Adjust as needed
        "top_p": 0.7,
        "top_k": 50,
    }

    output_buffer = ""


    for token_data in llm(
        prompt,
        logits_processor=LogitsProcessorList([PrintLogitsAndTokenProcessor( llm, tokenizer)]),
        max_tokens=2000,  # Maximum tokens to generate
        stop=[  # Matching your Ollama stop sequences
            "<|endoftext|>",
            "<|end|>",
            "<|user|>",
            "<|assistant|>",
        ],
        echo=True,  # Don't echo the prompt
        stream=True,  # Enable streaming
        **sampling_params
    ):

        # print(token_data)

        # token = token_data["token"]
        #logits = token_data["logits"]  # Logits for all vocabulary tokens
        #token_id = token_data["token_id"]

        # probabilities = np.exp(logits - np.max(logits))  # Softmax calculation
        # probabilities /= np.sum(probabilities)

        # Append the token to the generated text
        # output_buffer += token
        #print(f"Token: {token}, Probability: {probabilities[token_id]}")

        token_text = token_data['choices'][0]['text']
        output_buffer += token_text  # Add the token to the buffer

        print(token_text, end='', flush=True)

        # if END_SEARCH_QUERY in output_buffer:
        #    print("\n\nEND_SEARCH_QUERY detected. Stopping generation.")


    logging.info("\n\nGeneration complete.")

if __name__ == "__main__":
    main()

import logging
import llama_cpp
import ctypes
import numpy as np
from transformers import AutoTokenizer

prompt = """<|im_start|>system
You are a helpful and harmless assistant. You are Qwen developed by Alibaba. You should think step-by-step.<|im_end|>
<|im_start|>user
You are a reasoning assistant with the ability to perform web searches to help you answer the user's question accurately. You have special tools:

- To perform a search: write <|begin_search_query|> your query here <|end_search_query|>.
Then, the system will search and analyze relevant web pages, then provide you with helpful information in the format <|begin_search_result|> ...search results... <|end_search_result|>.

You can repeat the search process multiple times if necessary. The maximum number of search attempts is limited to 5.

Once you have all the information you need, continue your reasoning.

Example:
Question: "Who got the first Nobel Prize in Physics?"
Assistant thinking steps:
- I need to find out who was awarded the first Nobel Prize in Physics.

Assistant:
<|begin_search_query|>first Nobel Prize in Physics winner<|end_search_query|>

(System returns processed information from relevant web pages)

Assistant continues reasoning with the new information...

Remember:
- Use <|begin_search_query|> to request a web search and end with <|end_search_query|>.
- When done searching, continue your reasoning.

Please answer the following question. You should provide your final answer in the format \boxed{YOUR_ANSWER}.

Question:
What is Jimmy Carter's birthday?

<|im_end|>
<|im_start|>assistant"""

def sample_with_temperature(model, n_vocab, logits, temperature=0.7):

    logits_array = np.array([logits[i] for i in range(n_vocab)], dtype=np.float64)

    logits_array = logits_array / temperature

    logits_array = logits_array - np.max(logits_array)

    exp_logits = np.exp(logits_array)

    probs = exp_logits / np.sum(exp_logits)

    if not np.all(np.isfinite(probs)) or np.sum(probs) == 0:
        print("Warning: Invalid probabilities generated")
        return llama_cpp.llama_token_bos(model)

    next_token = np.random.choice(n_vocab, p=probs)

    next_token_logits = logits[next_token]

    print(f"Sampled token {next_token} with logits {next_token_logits}")

    buffer = ctypes.create_string_buffer(128)

    n_bytes = llama_cpp.llama_token_to_piece(
        model,
        next_token,
        buffer,
        128,
        0,
        True
    )

    if n_bytes > 0:
        piece = buffer.raw[:n_bytes].decode('utf-8', errors='replace')
        print(f"\nSampled token {next_token} -> '{piece}'")

    return next_token

def main():
    logging.basicConfig(level=logging.INFO)

    # tokenizer = AutoTokenizer.from_pretrained("/Users/hadfield/models/", trust_remote_code=True)
    # if tokenizer.pad_token is None:
    #    tokenizer.pad_token = tokenizer.eos_token
    # tokenizer.padding_side = 'left'

    prompt2 = """<|im_start|>system
You are a helpful and harmless assistant. You are Qwen developed by Alibaba. You should think step-by-step.<|im_end|>
<|im_start|>user
Hello there!  What is your name?
<|im_end|>
<|im_start|>assistant"""

    llama_cpp.llama_backend_init(numa=False)

    model_path = "/Users/hadfield/models/QwQ-32B-Preview-Q5_K_S.gguf"

    lparams = llama_cpp.llama_model_default_params()

    model = llama_cpp.llama_load_model_from_file(model_path.encode("utf-8"), lparams)

    SPECIAL_TOKENS = {
        'bos': 151643,  # <|endoftext|>
        'eos': 151645,  # <|im_end|>
        'eot': 151645,  # <|im_end|> (same as eos)
        'pad': 151643,  # <|endoftext|> (same as bos)
        'im_start': 151644,
    }

    bos_token = llama_cpp.llama_token_bos(model)
    eos_token = llama_cpp.llama_token_eos(model)
    nl_token = llama_cpp.llama_token_nl(model)

    # print(f"Special tokens:")
    # print(f"BOS token: {bos_token}")
    # print(f"EOS token: {eos_token}")
    # print(f"NL token: {nl_token}")

    # Let's see what these tokens translate to in text
    """
    buffer = ctypes.create_string_buffer(128)
    for token, name in [(bos_token, "BOS"), (eos_token, "EOS"), (nl_token, "NL")]:
        n_bytes = llama_cpp.llama_token_to_piece(
            model,
            token,
            buffer,
            128,
            0,
            True  # Set special=True for special tokens
        )
        if n_bytes > 0:
            piece = buffer.value.decode('utf-8', errors='replace')
            print(f"{name} token text: '{piece}' (hex: {buffer.raw[:n_bytes].hex()})")
    """

    stop_texts = [
        "<|endoftext|>",
        "<|end|>",
        "<|user|>",
        "<|assistant|>"
    ]

    # Create a buffer to store token IDs
    temp_tokens = (llama_cpp.llama_token * 8)()  # Buffer for tokenizing stop sequences
    stop_tokens = set()

    # Get token IDs for each stop sequence
    for stop_text in stop_texts:
        n = llama_cpp.llama_tokenize(
            model,
            stop_text.encode('utf-8'),
            len(stop_text),
            temp_tokens,
            8,  # max tokens - each stop sequence should be 1-2 tokens
            False,  # add_bos
            False  # special
        )
        # Add all tokens from the stop sequence
        for i in range(n):
            stop_tokens.add(temp_tokens[i])

    stop_tokens.add(bos_token)
    stop_tokens.add(eos_token)

    print("Stop tokens:", stop_tokens)

    # exit(0)

    # Set context size to 8K
    cparams = llama_cpp.llama_context_default_params()
    cparams.n_ctx = 8_000  # Set explicit context size

    n_vocab = llama_cpp.llama_n_vocab(model)

    ctx = llama_cpp.llama_new_context_with_model(model, cparams)

    text = prompt.encode("utf-8")
    text_len = len(text)

    n_ctx = 8_000
    tokens = (llama_cpp.llama_token * n_ctx)()  # Larger token array

    n_tokens = llama_cpp.llama_tokenize(
        model,
        text,
        text_len,
        tokens,
        n_ctx,
        False,
        True
    )

    print(f"Number of tokens: {n_tokens}")
    print("\nTokens:")
    for i in range(n_tokens):
        buffer = ctypes.create_string_buffer(128)
        n_bytes = llama_cpp.llama_token_to_piece(
            model,
            tokens[i],
            buffer,
            128,
            0,
            True  # Set special=True to handle special tokens
        )

        if n_bytes > 0:
            piece = buffer.raw[:n_bytes].decode('utf-8', errors='replace')
            print(f"Token {i}: {tokens[i]} -> '{piece}'")


    """
    print("\nSpecial token verification:")
    special_tokens = {
        'bos': llama_cpp.llama_token_bos(model),
        'eos': llama_cpp.llama_token_eos(model),
        'im_start': 151644,
        'im_end': 151645,
    }

    for name, token_id in special_tokens.items():
        buffer = ctypes.create_string_buffer(128)
        n_bytes = llama_cpp.llama_token_to_piece(
            model,
            token_id,
            buffer,
            128,
            0,
            True
        )
        if n_bytes > 0:
            piece = buffer.raw[:n_bytes].decode('utf-8', errors='replace')
            print(f"{name}: {token_id} -> '{piece}'")

    """

    """
    batch.n_tokens = n_tokens
    batch.token = (llama_cpp.llama_token * n_ctx)()
    batch.pos = (ctypes.c_int32 * n_ctx)()
    batch.n_seq_id = (ctypes.c_int32 * n_ctx)()
    batch.seq_id = ((ctypes.POINTER(ctypes.c_int32) * n_ctx))()
    seq_id = (ctypes.c_int32 * 1)()
    seq_id[0] = 0
    for i in range(n_ctx):
        batch.seq_id[i] = seq_id

    # Create logits as pointer to bytes
    logits_array = (ctypes.c_byte * n_ctx)()
    batch.logits = ctypes.cast(logits_array, ctypes.POINTER(ctypes.c_byte))

    # Copy tokens and set positions
    for i in range(n_tokens):
        batch.token[i] = tokens[i]
        batch.pos[i] = i
        batch.n_seq_id[i] = 1
        logits_array[i] = 1  # Set to 1 for True

    print("\nBatch setup:")
    print(f"n_tokens: {batch.n_tokens}")
    print(f"Last token: {batch.token[n_tokens - 1]}")
    print(f"Last position: {batch.pos[n_tokens - 1]}")
    print(f"Last logits flag: {logits_array[n_tokens - 1]}")

    # Perform decode
    ret = llama_cpp.llama_decode(ctx, batch)
    print(f"\nDecode return: {ret}")

    # Get and check logits immediately after decode
    logits = llama_cpp.llama_get_logits(ctx)
    if logits is not None:
        print("\nChecking first few logits values directly:")
        for i in range(10):
            print(f"Logit {i}: {logits[i]}")

        n_vocab = llama_cpp.llama_n_vocab(model)
        logits_array = np.array([logits[i] for i in range(n_vocab)])
        print(f"\nLogits distribution:")
        print(f"Number of non-zero logits: {np.count_nonzero(logits_array)}")
        if np.count_nonzero(logits_array) > 0:
            print(f"Non-zero max: {np.max(logits_array[logits_array != 0])}")
            print(f"Non-zero min: {np.min(logits_array[logits_array != 0])}")

    """
    # exit(0)

    batch = llama_cpp.llama_batch()

    # Allocate all batch fields to context size
    batch.token = (llama_cpp.llama_token * n_ctx)()
    batch.pos = (ctypes.c_int32 * n_ctx)()
    batch.n_seq_id = (ctypes.c_int32 * n_ctx)()

    # Create sequence array at context size
    sequence_array = (ctypes.c_int32 * n_ctx)()
    seq_id_array = (ctypes.POINTER(ctypes.c_int32) * n_ctx)()
    for i in range(n_ctx):
        seq_id_array[i] = ctypes.cast(sequence_array, ctypes.POINTER(ctypes.c_int32))

    batch.seq_id = seq_id_array

    # Create logits array at context size
    # thought this was float instead of byte, but that didnt work
    logits_array = (ctypes.c_byte * (n_ctx))()

    batch.logits = ctypes.cast(logits_array, ctypes.POINTER(ctypes.c_byte))

    # Process the initial tokens
    for i in range(n_tokens):
        batch.token[i] = tokens[i]
        batch.pos[i] = i
        batch.n_seq_id[i] = 1
        # setting this triggers random initial token
        # not setting it has logits all zero, we we can skip
        # logits_array[i] = 0 # 0xFF # do this?

    batch.n_tokens = n_tokens # -1 # subtracting one

    if llama_cpp.llama_decode(ctx, batch) != 0:
        raise RuntimeError("Failed to decode")

    # can't quite figure out how to force advancing
    # batch.pos[0] = n_tokens + 1
    # llama_cpp.llama_decode(ctx, batch)

    # logits = llama_cpp.llama_get_logits(ctx)
    # if logits is None or all(logit == 0.0 for logit in logits[:n_vocab]):
    #    raise RuntimeError("Logits buffer not populated after llama_decode")

    # Calculate remaining tokens for generation
    max_tokens = n_ctx - n_tokens
    generated = []
    n_past = n_tokens
    output_text = ""

    # Increase piece buffer size for potentially longer token outputs
    # PIECE_BUF_SIZE = 64  # Increased from 32

    for i in range(max_tokens):

        # n_vocab = llama_cpp.llama_n_vocab(model)

        logits = llama_cpp.llama_get_logits(ctx)

        if all(logit == 0.0 for logit in logits[:n_vocab]):
            print(f"Logits are all zero at step {i}, skipping to next iteration.")

            batch.n_tokens = 1
            batch.token[0] = tokens[-1]
            batch.pos[0] = n_past + i
            batch.n_seq_id[0] = 1

            # this seems necessary to trigger some recalculation
            logits_array[0] = 1

            # Decode next token
            if llama_cpp.llama_decode(ctx, batch) != 0:
                print("\n[Decode failed]")
                break

            continue  # Skip processing this step

        # next_token = max(range(n_vocab), key=lambda x: logits[x])

        next_token = sample_with_temperature(model, n_vocab, logits)

        buffer = ctypes.create_string_buffer(128)

        n_bytes = llama_cpp.llama_token_to_piece(
            model,
            next_token,
            buffer,
            128,
            0,
            False
        )

        if n_bytes > 0:
            piece = buffer.raw[:n_bytes].decode('utf-8', errors='replace')
            print(piece, end='', flush=True)
            output_text += piece

        # Check for special stop tokens
        if next_token in {151643, 151645}:  # BOS or EOS/EOT
            print("\n[Stopping on special token]")
            break

        # Update the batch for next token
        batch.token[0] = next_token
        batch.pos[0] = n_past + i
        batch.n_seq_id[0] = 1
        # logits_array[0] = 1
        batch.n_tokens = 1

        # Decode next token
        if llama_cpp.llama_decode(ctx, batch) != 0:
            print("\n[Decode failed]")
            break

    print("\n\nFinal collected output:", output_text)

    # Cleanup
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
    llama_cpp.llama_backend_free()

    exit(0)

    for i in range(max_tokens):
        logits = llama_cpp.llama_get_logits(ctx)
        n_vocab = llama_cpp.llama_n_vocab(model)

        # next_token = max(range(n_vocab), key=lambda x: logits[x])

        next_token = sample_with_temperature(model, n_vocab, logits)

        buffer = ctypes.create_string_buffer(128)

        n_bytes = llama_cpp.llama_token_to_piece(
            model,
            next_token,
            buffer,
            128,
            0,
            False
        )

        if n_bytes > 0:
            piece = buffer.value.decode('utf-8', errors='replace')
            print(piece, end='', flush=True)
            output_text += piece

        generated.append(next_token)

        # Check for special tokens
        if next_token in SPECIAL_TOKENS.values():
            token_name = [name for name, token in SPECIAL_TOKENS.items() if token == next_token][0]
            print(f"\n[Stopping on special token: {token_name} ({next_token})]")
            break

        batch.token[0] = next_token
        batch.pos[0] = n_past + i
        batch.n_seq_id[0] = 1
        logits_array[0] = 1
        batch.n_tokens = 1

        if llama_cpp.llama_decode(ctx, batch) != 0:
            print("\n[Context limit reached]")
            break

    print("\n\nFinal collected output:", output_text)

    # Cleanup
    llama_cpp.llama_free(ctx)
    llama_cpp.llama_free_model(model)
    llama_cpp.llama_backend_free()


if __name__ == "__main__":
    main()

"""
        if i == 0:
            print("\nFirst token logits analysis:")
            logits_array = np.array([logits[i] for i in range(n_vocab)])
            # Get top 20 tokens by probability
            top_indices = np.argsort(logits_array)[-20:][::-1]
            print("Top 20 tokens by logit value:")
            for idx in top_indices:
                buffer = ctypes.create_string_buffer(128)
                n_bytes = llama_cpp.llama_token_to_piece(
                    model,
                    idx,
                    buffer,
                    128,
                    0,
                    True
                )
                if n_bytes > 0:
                    piece = buffer.raw[:n_bytes].decode('utf-8', errors='replace')
                    print(f"Token {idx}: '{piece}', logit: {logits_array[idx]}")

"""

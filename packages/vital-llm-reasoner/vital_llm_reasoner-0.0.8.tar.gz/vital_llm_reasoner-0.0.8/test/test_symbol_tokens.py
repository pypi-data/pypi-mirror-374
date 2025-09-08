from transformers import AutoTokenizer
import tiktoken

# tokenizer = AutoTokenizer.from_pretrained("Qwen/QwQ-32B-Preview")
# tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1")

# tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Llama-70B")

# tokenizer = AutoTokenizer.from_pretrained("Valdemardi/DeepSeek-R1-Distill-Qwen-32B-AWQ")


# tokenizer = AutoTokenizer.from_pretrained("Valdemardi/DeepSeek-R1-Distill-Llama-70B-AWQ")

# Hugging Face tokenizer option
tokenizer = AutoTokenizer.from_pretrained("Qwen/QwQ-32B")

# OpenAI GPT-OSS 120B o200k_harmony tokenizer option
# This is a BPE tokenizer with 201,088 tokens, extended from o200k for harmony chat format
# oss_tokenizer = tiktoken.get_encoding("o200k_base")  # Using o200k_base as closest available

# Choose which tokenizer to use
use_oss_tokenizer = True  # Set to True to use OpenAI's o200k tokenizer

if use_oss_tokenizer:
    oss_tokenizer = tiktoken.get_encoding("o200k_base")
    print("Using OpenAI o200k_base tokenizer (closest to o200k_harmony)")
    
    symbols = ["◖", "◗", "◢", "◣", "◒", "◓","→","←","»","«"]
    for symbol in symbols:
        tokens = oss_tokenizer.encode(symbol)
        print(f"Symbol: {symbol}, Token IDs: {tokens}")
else:
    print("Using Hugging Face tokenizer")
    
    symbols = ["◖", "◗", "◢", "◣", "◒", "◓","→","←","»","«"]
    for symbol in symbols:
        tokens = tokenizer(symbol, return_tensors="pt")
        print(f"Symbol: {symbol}, Token IDs: {tokens.input_ids}")



exit(0)

"""
OSS
Symbol: →, Token IDs: [20216]
Symbol: ←, Token IDs: [75391]
Symbol: », Token IDs: [1924]
Symbol: «, Token IDs: [4244]
"""


# Token exploration loop - uncomment to explore token mappings
if use_oss_tokenizer:
    # o200k_base has ~200k tokens
    token_range = 201088  # Approximate token count for o200k_harmony
    current_tokenizer = oss_tokenizer
else:
    # Hugging Face tokenizer range
    token_range = 130000
    current_tokenizer = tokenizer

# for i in range(token_range):
#     if use_oss_tokenizer:
#         try:
#             tok = current_tokenizer.decode([i])
#         except:
#             continue
#     else:
#         tok = current_tokenizer.decode([i])
#     
#     if len(tok) > 0:
#         if tok != '�':
#             print(f"token({i}): '{tok}'")

# token(8674): '→'
# token(57258): '←'

# token(3807): '»'
# token(12389): '«'

# byte_sequence = b'\xe2\x85'
# byte_sequence = b'\xe2\x85\xa2'
# decoded_character = byte_sequence.decode('utf-8')
# print(decoded_character)

# decoded_text = tokenizer.decode([146634])
# print(f"Token ID 146634 decodes to: {decoded_text}")

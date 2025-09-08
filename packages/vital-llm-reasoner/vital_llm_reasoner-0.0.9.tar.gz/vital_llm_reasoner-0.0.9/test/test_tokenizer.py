from transformers import AutoTokenizer


def main():

    tokenizer = AutoTokenizer.from_pretrained(
        # "Qwen/QwQ-32B-Preview",
        "Qwen/QwQ-32B-AWQ",
        use_fast=True,
        add_prefix_space=True,
        trust_remote_code=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'left'

    text = """
        raise ValueError("Factorial is not defined for negative numbers.")
"""

    encoded = tokenizer.encode(text)

    print(encoded)

    for tok in encoded:
        print(f"{tok} = '{tokenizer.decode([tok])}'")

    decoded = tokenizer.decode(encoded)

    print(decoded)

if __name__ == "__main__":
    main()

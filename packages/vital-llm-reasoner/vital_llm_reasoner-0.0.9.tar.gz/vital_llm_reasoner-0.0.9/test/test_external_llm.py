import logging
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig


def main():
    logging.basicConfig(level=logging.INFO)

    config_file_path = "../reasoner_config.yaml"

    reasoner_config = ReasonerConfig(config_file_path)

    openai_api_key = reasoner_config.openai_key

    os.environ["OPENAI_API_KEY"] = openai_api_key

    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    input_messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is the capital of France?")
    ]

    response = llm.invoke(input_messages)

    assistant_response = response.content

    print("Assistant response:", assistant_response)


if __name__ == "__main__":
    main()

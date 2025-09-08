import logging
import os
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.code_executor_member import CodeExecutorMember
from vital_llm_reasoner.ensemble.member.llm_member import LLMMember
from vital_llm_reasoner.ensemble.member.logic_query_member import LogicQueryMember
from vital_llm_reasoner.ensemble.member.web_search_member import WebSearchMember
from vital_llm_reasoner.ensemble.process.orchestrator import Orchestrator
from vital_llm_reasoner.reasoner.qwq_reasoner import QWQReasoner
from vital_llm_reasoner.reasoner.r1_reasoner import R1Reasoner


def main():
    logging.basicConfig(level=logging.INFO)

    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    config_file_path = "../reasoner_config.yaml"

    reasoner_config = ReasonerConfig(config_file_path)

    model_path = "/Users/hadfield/models/DeepSeek-R1-Distill-Llama-70B-Q3_K_M.gguf"

    # this path doesn't work, using the hugging face model directly in the code
    tokenizer_path = "/Users/hadfield/models/r1_tokenizer/"

    # Check if model exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}")

    user_message_1 = "What is Jimmy Carter's birthday?"

    user_message_2 = """
Solve this puzzle and be concise in your reasoning.

Selena, Jennifer and Miley wear a blue dress, yellow dress, and green dress in an unknown order. It is known that:

1) If Selena wears blue, then Jennifer wears green.
2) If Selena wears yellow, then Miley wears green.
3) If Jennifer does not wear yellow, then Miley wears blue.

What is the color of the dress Selena is wearing?
"""

    user_message_3 = """
How many companies does Elon Musk currently run?
List them.
Support your answer with evidence for each in the list from trusted sources.
Be thorough.
"""

    user_message_4 = """
Write python code and run it using the code execution tool to calculate the factorial of 20.  
I want to know the complete output of the program when you run it.  
"""

    user_message_5 = """
Calculate the factorial of 20.  
"""

    user_message_6 = """
Give me a list of my friends.
"""

    user_message_7 = """
    Give me a list of the addresses of all my friends.
    """

    # Tell me the confirmation code of running the code executor.

    user_message_8 = """
       Use your assistant to write code to calculate a factorial and then use the code executor to run it to calculate the factorial of 20.
       """


    # Notes:
    # orchestrator is meant to be re-used for different requests
    # init-ing members might be heavy so should be re-used
    # a given call may include a JWT token and other state such as user id.

    # these would need to be captured by the server (vLLM) when a request is posted
    # and passed in on the request for:
    # handle_user_message()

    user_message = user_message_1

    web_search_member = WebSearchMember(config=reasoner_config)
    logic_query_member = LogicQueryMember(config=reasoner_config)
    code_execution_member = CodeExecutorMember(config=reasoner_config)
    llm_member = LLMMember(config=reasoner_config)

    orchestrator = Orchestrator(config=reasoner_config)

    reasoner = R1Reasoner(tokenizer_path=tokenizer_path, model_path=model_path)

    orchestrator.set_reasoner(reasoner)

    orchestrator.add_member(web_search_member)
    orchestrator.add_member(logic_query_member)
    orchestrator.add_member(code_execution_member)
    orchestrator.add_member(llm_member)

    agent_message = orchestrator.handle_user_message(user_message)

    print("")

    print(f"Agent message: {agent_message}")

if __name__ == "__main__":
    main()

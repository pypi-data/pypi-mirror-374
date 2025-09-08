import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag


# abstract class for LLMs, either local or remote
# initially use specifically for 4o-mini

class LLMMember(EnsembleMember):

      def __init__(self, *, config: ReasonerConfig | None = None):
            super().__init__(config=config)

            openai_api_key = self.config.openai_key
            os.environ["OPENAI_API_KEY"] = openai_api_key

      @classmethod
      def get_task_tag(cls) -> TaskTag:
            task_tag = TaskTag('llm_request')
            return task_tag


      def handle_inquiry(self, inquiry: Inquiry, context: str = None) -> Answer:
            inquiry_string = inquiry.inquiry

            answer_string = "No answer"

            # include current context so far?

            llm_instructions = """
You are an assistant to an A.I. Agent.
You respond to the request using your best ability, and explain if you cannot fulfill the request.
The A.I. Agent may have tools and need your help to compose inputs to those tools.
"""

            try:

                  user_message = f"""
Respond to the request:
--------------------
{inquiry_string}
--------------------
Response in the format:
--------------------
Answer:
*put your answer here*
--------------------                           
"""

                  llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

                  input_messages = [
                        SystemMessage(content=llm_instructions),
                        HumanMessage(content=user_message)
                  ]

                  response = llm.invoke(input_messages)

                  assistant_response = response.content

                  # print("Assistant response:\n", assistant_response)

                  answer_string = assistant_response

            except Exception as e:
                  error = f"Error calling LLM: {type(e).__name__}: {e}"
                  answer_string = error

            answer = Answer(
                  inquiry=inquiry,
                  answer=answer_string
            )

            return answer



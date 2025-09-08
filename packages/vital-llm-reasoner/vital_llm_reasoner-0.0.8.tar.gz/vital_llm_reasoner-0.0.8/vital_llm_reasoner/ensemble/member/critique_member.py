import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag
from vital_llm_reasoner.ensemble.process.logits_default_processor import LogitsDefaultProcessor
from vital_llm_reasoner.reasoner.ensemble_prompt import EnsemblePrompt
from vital_llm_reasoner.reasoner.ensemble_reasoner import EnsembleReasoner


class CritiqueMember(EnsembleMember):

      def __init__(self, *, orchestrator, reasoner: EnsembleReasoner, config: ReasonerConfig | None = None):
            super().__init__(config=config)

            self.reasoner = reasoner
            self.orchestrator = orchestrator

      @classmethod
      def get_task_tag(cls) -> TaskTag:
            task_tag = TaskTag('critique_request')
            return task_tag


      def handle_inquiry(self, inquiry: Inquiry, context: str = None) -> Answer:
            inquiry_string = inquiry.inquiry

            answer_string = "No answer"

            # include current context so far?

            # need ot pass in the full prompt for the emsemble member documentation?


            llm_instructions = """
You are an assistant to an A.I. Agent.
You critique the plan and provide feedback given to you.
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

                logits_processor = LogitsDefaultProcessor(
                    orchestrator=self.orchestrator,
                    llm=self.reasoner.get_llm(),
                    tokenizer=self.reasoner.get_tokenizer()
                )

                prompt_list = [{"role": "user", "content": llm_instructions + user_message}]

                prompt = EnsemblePrompt(prompt=prompt_list)

                output_buffer = ""

                token_generator = self.reasoner.generate_tokens(prompt, logits_processor)

                for token_data in token_generator:
                    token_text = token_data['choices'][0]['text']
                    output_buffer += token_text

                    print(token_text, end='', flush=True)

                answer_string = output_buffer

            except Exception as e:
                  error = f"Error calling LLM: {type(e).__name__}: {e}"
                  answer_string = error

            answer = Answer(
                  inquiry=inquiry,
                  answer=answer_string
            )

            return answer

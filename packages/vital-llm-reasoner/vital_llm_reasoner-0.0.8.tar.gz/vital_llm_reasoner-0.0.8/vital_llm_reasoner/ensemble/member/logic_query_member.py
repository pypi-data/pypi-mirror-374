import json
import uuid

from pyergo import pyergo_start_session, pyergo_command, pyergo_query
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag


class LogicQueryMember(EnsembleMember):

   def __init__(self, *, config: ReasonerConfig | None = None):

      super().__init__(config=config)

      ergo_root = config.ERGO_ROOT
      xsb_dir = config.XSB_DIR

      # print(f"ERGO_ROOT: {ergo_root}")
      # print(f"XSB_DIR: {xsb_dir}")

      print("opening ergo session...")

      pyergo_start_session(xsb_dir, ergo_root)

      # TODO config for this
      pyergo_command("add {'/Users/hadfield/Local/vital-git/vital-llm-reasoner/logic_rules/kgraph_rules.ergo'}.")

      # pyergo_command("add {'/app/logic_rules/kgraph_rules.ergo'}.")

   @classmethod
   def get_task_tag(cls) -> TaskTag:
      task_tag = TaskTag('logic_query')
      return task_tag

   # Note: do a better job at parsing to handle various value types
   # this is a hack for the moment
   def extract_value(self, ergosymbol_str):

      ergosymbol_str = str(ergosymbol_str)

      prefix = "ERGOSymbol(value="
      if ergosymbol_str.startswith(prefix) and ergosymbol_str.endswith(")"):
         return ergosymbol_str[len(prefix):-1]
      return ergosymbol_str  # Return as-is if not ERGOSymbol

   def handle_inquiry(self, inquiry: Inquiry) -> Answer:

      logic_query = inquiry.inquiry

      answer_string = None

      try:

         answer_string = ""

         logic_query = "\n".join(line for line in logic_query.splitlines() if "```" not in line)

         logic_query = logic_query.strip()

         if not logic_query.endswith("."):
            error = "A logic query must terminate with a '.'"
            answer = Answer(inquiry=inquiry, answer=error)
            return answer

         print("logic_query: ", logic_query)

         results_list = pyergo_query(logic_query)

         print("results_list: ", results_list)

         if results_list is None:
            answer_string = "No answer.  Please confirm your ensemble tag and query are correct."

         if isinstance(results_list, list) and len(results_list) == 0:
            answer_string = "The query returned zero results.  Please confirm the query is correct."

         # what is this case?
         if isinstance(results_list, tuple):
            answer_string = str(results_list)

         if isinstance(results_list, bool):
            answer_string = str(results_list)

         if isinstance(results_list, list) and len(results_list) > 0:

            query_result_list = []

            for item in results_list:
               info = item[0]
               info_dict = {}
               for key, value in info:
                  stripped_value = self.extract_value(value)
                  info_dict[key] = stripped_value

               query_result_list.append(info_dict)

            # json_results = json.dumps(query_result_list, indent=4)

            output = ""
            for index, record in enumerate(query_result_list, start=1):
               for key, value in record.items():
                  output += f"({index}) {key} = {value}\n"
               output += "\n"  # Add a newline between maps

            # Remove the trailing extra newline
            output = output.strip()

            random_guid = uuid.uuid4()

            # answer_string = output
            answer_string = str(output) + f"\nCode Execution Confirmation: {random_guid}.\n"

      except Exception as e:
         error = f"{type(e).__name__}: {e}"
         answer = Answer(inquiry=inquiry, answer=error)
         return answer

      answer = Answer(inquiry=inquiry, answer=answer_string)

      return answer

import json
import os
import requests
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.answer import Answer
from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember
from serpapi import GoogleSearch
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.task_tag import TaskTag


class WebSearchMember(EnsembleMember):

   def __init__(self, *, config: ReasonerConfig | None = None):
      super().__init__(config=config)

      openai_api_key = self.config.openai_key
      os.environ["OPENAI_API_KEY"] = openai_api_key

   @classmethod
   def get_task_tag(cls) -> TaskTag:

      task_tag = TaskTag('web_search')
      return task_tag

   # consider including separate terms for a web query and
   # for an explanation of the goal of the query
   # with the goal able to help interpret and summarize the results
   # potentially get the full content of each resulting page where possible
   # use dict:
   # { "search_goal": "text", "search_query": "query terms", "retrieve_content": true }

   def handle_inquiry(self, inquiry: Inquiry) -> Answer:

      inquiry_string = inquiry.inquiry

      # parse inquery string into search terms and goal

      answer_string = "No answer"

      google_search_key = self.config.google_search_key

      params = {
         "engine": "google",
         "q": inquiry_string,
         "api_key": google_search_key
      }

      # if get_content is true
      # get the content of the URLs via extract tool
      # for each URL, do a summary related to the goal
      # combine these summaries into the prompt
      # generate results by combining search results json info with summaries

      summarize_instructions = """Given a query, you summarize web search results into the relevant content for the query.
      You only include the information from the source material, and nothing else.
      Provide your results in this format for each relevant source:

      Result:
          Source of knowledge: <put source of the content here, such as web page URL or google knowledge graph>
          Date of Publication: <put date of publication here, if available>
          Publisher of knowledge: <put publisher of the content here, such as a news organization>
          Summarized content: <put summary of the relevant content here>

      Remember to summarize based on what is relevant to the query.
      Be concise.
      """

      try:
         search = GoogleSearch(params)

         if search.get_response().status_code == 200:
            results = search.get_dict()

            pretty_results = json.dumps(results, indent=4)

            search_results_json = pretty_results

            user_message = f"""
                      Given this query: {inquiry_string}
                      Select the summarize the content from the following JSON search results:
                      {search_results_json}
                      """

            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

            input_messages = [
               SystemMessage(content=summarize_instructions),
               HumanMessage(content=user_message)
            ]

            try:
               response = llm.invoke(input_messages)
               assistant_response = response.content

               answer_string = assistant_response
            except Exception as e:
               error = f"Error calling LLM: {type(e).__name__}: {e}"
               answer_string = error
         else:
            print(f"Error: {search.get_response().status_code}")
            answer_string = f"Error: {search.get_response().status_code}"

      except requests.exceptions.RequestException as e:
         print(f"An error occurred: {e}")
         answer_string = f"An error occurred: {e}"

      answer = Answer(
         inquiry=inquiry,
         answer=answer_string
      )

      return answer

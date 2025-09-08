import json
import logging
import os
import requests
from serpapi import GoogleSearch
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI


def main():
    logging.basicConfig(level=logging.INFO)

    config_file_path = "../reasoner_config.yaml"
    reasoner_config = ReasonerConfig(config_file_path)

    openai_api_key = reasoner_config.openai_key

    os.environ["OPENAI_API_KEY"] = openai_api_key

    google_search_key = reasoner_config.google_search_key

    # query = "when is Jimmy Carter's Birthday"

    # query = "education of bill clinton"

    query = "companies run by elon musk"

    params = {
        "engine": "google",
        "q": query,
        "api_key": google_search_key
    }

    summarize_instructions = """Given a query, you summarize web search results into the relevant content for the query.
You only include the information from the source material, and nothing else.
Provide your results in this format for each relevant source:
    
Result:
    Source of knowledge: <put source of the content here, such as web page URL or google knowledge graph>
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

            print(pretty_results)

            organic_results = results["organic_results"]

            print(organic_results )

            search_results_json = pretty_results

            user_message = f"""
                Given this query: {query}
                Select the summarize the content from the following JSON search results:
                {search_results_json}
                """

            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

            input_messages = [
                SystemMessage(content=summarize_instructions),
                HumanMessage(content=user_message)
            ]

            response = llm.invoke(input_messages)

            assistant_response = response.content

            print("Assistant response:\n", assistant_response)

        else:
            print(f"Error: {search.get_response().status_code}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()

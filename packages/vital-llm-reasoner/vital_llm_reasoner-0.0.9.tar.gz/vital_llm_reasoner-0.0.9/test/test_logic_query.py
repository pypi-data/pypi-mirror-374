import json
import re
from pyergo import pyergo_start_session, pyergo_command, pyergo_query, pyergo_end_session
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig


def extract_value(ergosymbol_str):

    ergosymbol_str = str(ergosymbol_str)

    prefix = "ERGOSymbol(value="
    if ergosymbol_str.startswith(prefix) and ergosymbol_str.endswith(")"):
        return ergosymbol_str[len(prefix):-1]
    return ergosymbol_str  # Return as-is if not ERGOSymbol


def main():


    config_file_path = "../reasoner_config.yaml"
    reasoner_config = ReasonerConfig(config_file_path)


    ergo_root = reasoner_config.ERGO_ROOT
    xsb_dir = reasoner_config.XSB_DIR

    pyergo_start_session(xsb_dir, ergo_root)
    pyergo_command("writeln('Hello World!')@\\plg.")
    pyergo_command("add {'/Users/hadfield/Local/vital-git/vital-llm-reasoner/logic_rules/kgraph_rules.ergo'}.")

    query = """
    
    friend(?Friend), get_friend(?Friend, ?FriendString).
    
    """

    query = query.strip()

    results_list = pyergo_query(query)

    print(results_list)

    result_list = []

    for item in results_list:
        info = item[0]
        info_dict = {}
        for key, value in info:
            stripped_value = extract_value(value)
            info_dict[key] = stripped_value

        # Append each processed dictionary to the result list
        result_list.append(info_dict)

    print(result_list)

    json_results = json.dumps(result_list,  indent=4)

    print(json_results)

    pyergo_end_session()

if __name__ == "__main__":
    main()


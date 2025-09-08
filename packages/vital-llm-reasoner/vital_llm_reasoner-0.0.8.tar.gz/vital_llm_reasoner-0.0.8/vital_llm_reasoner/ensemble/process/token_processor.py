import re
from llama_cpp import LogitsProcessor, Llama, LogitsProcessorList
from vital_llm_reasoner.config.reasoner_config import ReasonerConfig
from vital_llm_reasoner.ensemble.member.code_executor_member import CodeExecutorMember
from vital_llm_reasoner.ensemble.member.inquiry import Inquiry
from vital_llm_reasoner.ensemble.member.llm_member import LLMMember
from vital_llm_reasoner.ensemble.member.logic_query_member import LogicQueryMember
from vital_llm_reasoner.ensemble.member.web_search_member import WebSearchMember
from vital_llm_reasoner.ensemble.process import orchestrator
from vital_llm_reasoner.reasoner.ensemble_reasoner import EnsembleReasonerType

SEARCH_QUERY = "search_query"
SEARCH_RESULT = "search_result"

LOGIC_QUERY = "logic_query"
LOGIC_RESULT = "logic_result"

CODE_EXECUTION = "code_execution"
CODE_RESULT = "code_result"

# Define special tokens
BEGIN_SEARCH_QUERY = f"<{SEARCH_QUERY}>"
END_SEARCH_QUERY = f"</{SEARCH_QUERY}>"

BEGIN_SEARCH_RESULT = "<ensemble:search_result>"
END_SEARCH_RESULT = "</ensemble:search_result>"

BEGIN_CODE_RESULT = "<ensemble:code_result>"
END_CODE_RESULT = "</ensemble:code_result>"

BEGIN_LLM_RESULT = "<ensemble:llm_result>"
END_LLM_RESULT = "</ensemble:llm_result>"

BEGIN_LOGIC_QUERY_RESULT = "<ensemble:logic_query_result>"

END_LOGIC_QUERY_RESULT = "</ensemble:logic_query_result>"

# END_SEARCH_STRING = f"{END_SEARCH_QUERY}◗"

# using these in the prompt for starting/ending thoughts didn't work
# LOWER_CIRCLE = 149410
# UPPER_CIRCLE = 147754

# inject ensemble result

# correct information
# search_result = "Jimmy Carter's birthday is: October 1, 1924"

# wrong information
# ensemble_result = "Jimmy Carter's birthday is: December 21, 1920"

# it will believe info from the search results compared with its own memory
# things go off the rails when search results do not directly follow request

"""
OSS
Symbol: →, Token IDs: [20216]
Symbol: ←, Token IDs: [75391]
Symbol: », Token IDs: [1924]
Symbol: «, Token IDs: [4244]
"""


class TokenProcessor(LogitsProcessor):
    def __init__(self, orchestrator, reasoner_type, llm: Llama, tokenizer, *, config:ReasonerConfig=None):

        from vital_llm_reasoner.ensemble.process.orchestrator import Orchestrator
        assert isinstance(orchestrator, Orchestrator)

        self.orchestrator = orchestrator
        self.llm = llm
        self.tokenizer = tokenizer  # Pass the tokenizer to decode tokens
        self.gen_buffer = ""
        self.result_count = 0
        self.config=config
        self.ensemble_result = None
        self.ensemble_result_tokens = None
        self.reasoner_type = reasoner_type

    def __call__(self, input_ids, scores):
        # Decode the current token from input_ids
        if input_ids.size > 0:
            current_token_id = input_ids[-1]
            current_token = self.tokenizer.decode([current_token_id])
        else:
            current_token_id = 0
            current_token = "" # "<No input IDs yet>"

        START_TOOL_RESULTS = None
        END_TOOL_RESULTS = None

        END_TOOL_CALL = None
        CLOSE_CALL_TOOL = None

        OPEN_RESULTS_TOOL = None
        CLOSE_RESULTS_TOOL = None

        # print(f"Reasoner Type: {self.reasoner_type}")

        if self.reasoner_type == EnsembleReasonerType.QWQ_REASONER:
            # QWQ
            START_TOOL_CALL = 148320
            END_TOOL_CALL = 146152

            # QWQ
            START_TOOL_RESULTS = 146634
            END_TOOL_RESULTS = 146877

            OPEN_CALL_TOOL = '◖'
            CLOSE_CALL_TOOL = '◗'

            # QWQ
            OPEN_RESULTS_TOOL = '◢'
            CLOSE_RESULTS_TOOL = '◣'

        if self.reasoner_type == EnsembleReasonerType.R1_REASONER:
            # R1
            START_TOOL_CALL = 52118
            END_TOOL_CALL = 72958

            # R1
            START_TOOL_RESULTS = 13289
            END_TOOL_RESULTS = 24633

            OPEN_CALL_TOOL = '→'
            CLOSE_CALL_TOOL = '←'

            # R1
            OPEN_RESULTS_TOOL = '»'
            CLOSE_RESULTS_TOOL = '«'


        if self.reasoner_type == EnsembleReasonerType.OSS_REASONER:
            # OSS
            START_TOOL_CALL = 20216
            END_TOOL_CALL = 75391

            # OSS
            START_TOOL_RESULTS = 1924
            END_TOOL_RESULTS = 4244

            OPEN_CALL_TOOL = '→'
            CLOSE_CALL_TOOL = '←'

            # OSS
            OPEN_RESULTS_TOOL = '»'
            CLOSE_RESULTS_TOOL = '«'

        # token(52118): '→'
        # token(72958): '←'

        # token(8674): '→'
        # token(57258): '←'

        # token(8674): '→'
        # token(57258): '←'

        # print(f"current token: {current_token_id} : '{current_token}'")

        self.gen_buffer += current_token

        # can't generate start and end tool call
        # unless we are inserting it

        scores[START_TOOL_RESULTS] = -float('inf')
        scores[END_TOOL_RESULTS] = -float('inf')

        tokens = None

        # Note: currently this gets stuck after END_CIRCLE
        # unless we substitute a result
        # which is correct
        # however we may want it to continue reasoning until
        # it can't progress without the result.
        # so potentially prompt would help with that


        pattern = rf"</ensemble:([^>]+)>{CLOSE_CALL_TOOL}"

        # Search for the last match
        matches = list(re.finditer(pattern, self.gen_buffer))

        # print(f"buffer: {self.gen_buffer}")

        if current_token_id == END_TOOL_CALL:
            # print("End tool call")
            # print(f"buffer: {self.gen_buffer}")
            pass


        # look for new request or inserting tokens from existing one
        if (current_token_id == END_TOOL_CALL and matches and matches[-1].group(0).endswith(CLOSE_CALL_TOOL)) or self.ensemble_result is not None:

            # the closing symbol is needed otherwise the closing request is confused with the closing result
            ensemble_pattern = rf"</ensemble:([^>]+)>{CLOSE_CALL_TOOL}"

            matches = list(re.finditer(ensemble_pattern, self.gen_buffer, re.DOTALL))

            last_match = matches[-1].group(1) if matches else None

            # print("Last tag content:", last_match)

            if last_match == "search_query":

                if self.ensemble_result is None:

                    ensemble_search = self.orchestrator.get_member_by_tag( WebSearchMember.get_task_tag().member_name)

                    pattern = r"<ensemble:search_query>(.*?)</ensemble:search_query>"

                    matches = list(re.finditer(pattern, self.gen_buffer))
                    last_match = matches[-1].group(1) if matches else None

                    search_query = last_match

                    inquiry = Inquiry(member="web_search", inquiry=search_query)

                    answer = ensemble_search.handle_inquiry(inquiry)

                    answer_string = answer.answer

                    encoded_search_result = f"\n{OPEN_RESULTS_TOOL}{BEGIN_SEARCH_RESULT}{answer_string}{END_SEARCH_RESULT}{CLOSE_RESULTS_TOOL}"

                    # print(f"<encoded_search_result>{encoded_search_result}</search_result>")

                    self.ensemble_result = encoded_search_result

                    tokens = self.tokenizer.encode(self.ensemble_result)

                    self.ensemble_result_tokens = tokens

                    self.result_count = 0

                else:
                    tokens = self.ensemble_result_tokens

            if last_match == "code_execution":

                if self.ensemble_result is None:

                    ensemble_code_executor = self.orchestrator.get_member_by_tag( CodeExecutorMember.get_task_tag().member_name)

                    begin_pattern = r"<ensemble:code_execution>"
                    end_pattern = r"</ensemble:code_execution>"

                    begin_matches = list(re.finditer(begin_pattern, self.gen_buffer))

                    last_begin = begin_matches[-1].end()

                    end_match = re.search(end_pattern, self.gen_buffer[last_begin:])

                    start_pos = last_begin
                    end_pos = last_begin + end_match.start()
                    code_string = self.gen_buffer[start_pos:end_pos]

                    # print(f"<code>{code_string}</code>")

                    inquiry = Inquiry(member="code_executor", inquiry=code_string)

                    answer = ensemble_code_executor.handle_inquiry(inquiry)

                    answer_string = answer.answer

                    encoded_code_result = f"\n{OPEN_RESULTS_TOOL}{BEGIN_CODE_RESULT}{answer_string}{END_CODE_RESULT}{CLOSE_RESULTS_TOOL}"

                    # print(f"<code>{encoded_code_result}</code>")

                    self.ensemble_result = encoded_code_result

                    tokens = self.tokenizer.encode(self.ensemble_result)

                    # print(f"tokens: {tokens}")

                    self.ensemble_result_tokens = tokens

                    self.result_count = 0

                else:

                    tokens = self.ensemble_result_tokens

            if last_match == "logic_query":

                if self.ensemble_result is None:

                    ensemble_logic_query_executor = self.orchestrator.get_member_by_tag( LogicQueryMember.get_task_tag().member_name)

                    begin_pattern = r"<ensemble:logic_query>"
                    end_pattern = r"</ensemble:logic_query>"

                    begin_matches = list(re.finditer(begin_pattern, self.gen_buffer))

                    last_begin = begin_matches[-1].end()

                    end_match = re.search(end_pattern, self.gen_buffer[last_begin:])

                    start_pos = last_begin
                    end_pos = last_begin + end_match.start()
                    logic_query_string = self.gen_buffer[start_pos:end_pos]

                    print(f"<logic_query>{logic_query_string}</logic_query>")

                    inquiry = Inquiry(member="logic_query_executor", inquiry=logic_query_string)

                    answer = ensemble_logic_query_executor.handle_inquiry(inquiry)

                    answer_string = answer.answer

                    encoded_logic_query_result = f"\n{OPEN_RESULTS_TOOL}{BEGIN_LOGIC_QUERY_RESULT}{answer_string}{END_LOGIC_QUERY_RESULT}{CLOSE_RESULTS_TOOL}"

                    print(f"<logic_query_result>{encoded_logic_query_result}</logic_query_result>")

                    self.ensemble_result = encoded_logic_query_result

                    tokens = self.tokenizer.encode(self.ensemble_result)

                    # print(f"tokens: {tokens}")

                    self.ensemble_result_tokens = tokens

                    self.result_count = 0

                else:

                    tokens = self.ensemble_result_tokens


            if last_match == "llm_request":

                if self.ensemble_result is None:

                    ensemble_llm_member = self.orchestrator.get_member_by_tag( LLMMember.get_task_tag().member_name)

                    begin_pattern = r"<ensemble:llm_request>"
                    end_pattern = r"</ensemble:llm_request>"

                    begin_matches = list(re.finditer(begin_pattern, self.gen_buffer))

                    last_begin = begin_matches[-1].end()

                    end_match = re.search(end_pattern, self.gen_buffer[last_begin:])

                    start_pos = last_begin
                    end_pos = last_begin + end_match.start()
                    llm_request_string = self.gen_buffer[start_pos:end_pos]

                    print(f"<llm_request>{llm_request_string}</llm_request>")

                    inquiry = Inquiry(member="llm_member", inquiry=llm_request_string)

                    answer = ensemble_llm_member.handle_inquiry(inquiry)

                    answer_string = answer.answer

                    encoded_llm_result = f"\n{OPEN_RESULTS_TOOL}{BEGIN_LLM_RESULT}{answer_string}{END_LLM_RESULT}{CLOSE_RESULTS_TOOL}"

                    print(f"<llm_result>{encoded_llm_result}</llm_result>")

                    self.ensemble_result = encoded_llm_result

                    tokens = self.tokenizer.encode(self.ensemble_result)

                    # print(f"tokens: {tokens}")

                    self.ensemble_result_tokens = tokens

                    self.result_count = 0

                else:

                    tokens = self.ensemble_result_tokens

            # add tokens from any ensemble member that added them
            if tokens and self.result_count < len(tokens):

                # saving state is useful for reverting to an easier state
                # without having to recalculate everything
                # saved_state = self.llm.save_state()
                # state_size = saved_state.llama_state_size
                # print(f"Saved state size: { state_size / (1024 * 1024):.2f} MB")
                # self.llm.load_state(self.saved_state)
                # saved_state = None

                scores[:] = -float('inf')  # Mask all tokens

                token_id = tokens[self.result_count] # self.tokenizer.encode(tokens[self.result_count])[0]

                scores[token_id] = float('inf')

                token_string = self.tokenizer.decode([token_id])

                # print(f"Adding Token {self.result_count} of {len(tokens)}: '{token_string}' : {token_id}")

                self.result_count += 1

                if self.result_count >= len(tokens):
                    # reset
                    # print(f"Resetting result count at: {self.result_count} of {len(tokens)}")
                    self.result_count = 0
                    self.ensemble_result = None
                    self.ensemble_result_tokens = None

                return scores

        # probabilities = np.exp(scores - np.max(scores))  # Stabilized softmax
        # probabilities /= np.sum(probabilities)
        # print("Probabilities:", probabilities)

        return scores

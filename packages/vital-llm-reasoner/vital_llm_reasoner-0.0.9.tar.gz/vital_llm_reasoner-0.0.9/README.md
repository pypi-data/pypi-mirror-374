# vital-llm-reasoner

Very much work in progress

Needs to do:
playwright install 

# Ensemble Reasoning

Implementation to address deployment in:
Llama.cpp: CPU and GPU
vLLM: GPU
transformers (huggingface): GPU, baseline for ensemble attention implementation?

Initially all ensemble calls are synchronous and initiated by the LLM Reasoner

# Version 1 Magic Tokens

start ensemble call
end ensemble call

start ensemble result
end ensemble result

# Version 1 Tags

<ensemble:member_request>
</ensemble:member_request>

<ensemble:member_response>
</ensemble:member_response>

member is one of:
web_search
wikidata_search
kgraph_search
kgraph_traverse
logic_query
code_executor
llm

logic_query terms for testing:
friend(?Friend)
search_friends('search term', ?Friend)
get_friend('friend_uri', ?Friend)
traverse('uri', ?Node)
traverse_incoming('uri', ?Node)
traverse_outgoing('uri', ?Node)

# Version 2 Tags
# Use JSON Schema
 include request id
 
Potentially handle async cases with:
1) initial ensemble call
2) acknowledgement
3) result 

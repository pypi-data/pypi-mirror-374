from vital_llm_reasoner.ensemble.member.llm_member import LLMMember


# use langchain/langgraph to access external LLM
# such as 4o-mini
class EvidenceExtractionMember(LLMMember):
    pass

    # given question and document text, use LLM to extract
    # relevant parts of the document
    # also may clean up content, such as HTML


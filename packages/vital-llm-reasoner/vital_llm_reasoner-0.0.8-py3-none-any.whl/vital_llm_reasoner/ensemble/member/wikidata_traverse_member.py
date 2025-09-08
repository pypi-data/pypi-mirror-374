from vital_llm_reasoner.ensemble.member.ensemble_member import EnsembleMember

class WikidataTraverseMember(EnsembleMember):
    pass

    # given entity and description(s) of desired info
    # do vector search of wikidata properties to find
    # relevant ones and do sparql to retrieve
    # potentially do sparql to get list of available property types
    # then filter those via vector search, then query for the data of the relevant properties
    # similar process to kgraph service except wikidata properties instead of frames

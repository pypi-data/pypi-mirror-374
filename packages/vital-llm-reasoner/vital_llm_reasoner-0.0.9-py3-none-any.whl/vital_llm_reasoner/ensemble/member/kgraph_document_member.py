

# handle cases of document search, getting document content, etc.

# seperated out from kgraph_query to localize access to the file content data
# may be used internally with members like github to search for the content via
# kgraph, get the content via kgraphservice and the git repo,
# and potentially writing back to the git repo, updating the search index

# writing back could be handled with tool calling at conclusion of reasoning
# but if files are updated they need to be stored somewhere
# and github tracks changes, so maybe it makes sense to write them there directly
# and can always revert changes if needed





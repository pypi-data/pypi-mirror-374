
class EnsembleTool:
    pass

# Note: Tool Implementations
# Some tools will execute locally within the reasoner
# other tools will use an API client to access a tool remotely
# for testing purposes, a local tool may be defined with an API client
# intended to use in production

# authentication to a tool or remote client api can be handled
# via a JWT included in the reasoner request
# config file may define secrets like API Keys
# implementation can check if JWT provides access to a tool which uses an underlying api key
# production scenario would direct remote tools to api gateway
# which would enforce the jwt



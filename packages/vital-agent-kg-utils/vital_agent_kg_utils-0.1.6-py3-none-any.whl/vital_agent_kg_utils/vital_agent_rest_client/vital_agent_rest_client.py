
class VitalAgentRestClient:
    pass

# client to the groovy rest webservice which can write to the kgraph
# writing to the kgraph can trigger updates to the graph and vector dbs
# to keep these in sync
# an agent may not have write access to the kgraph but only read access
# via the resource client

# an agent may send messages to the processor which opened the websocket
# to the agent and request updates to the kgraph
# in which case the processor will make such changes and potentially
# trigger updates to the kgraph service (graph db and vector db)

# the extraction service uses this to write to the kgraph, which
# would update the sql db plus the graph and vector dbs
# so the path in this case would be:
# agent --> extraction service --> kgraph (sql, vector, graph)

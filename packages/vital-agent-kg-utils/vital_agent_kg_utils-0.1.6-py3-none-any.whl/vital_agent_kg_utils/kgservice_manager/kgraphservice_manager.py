

# wrapper around:
# vital_agent_rest_client and vital_agent_rest_resource_client
# for updating kgraph data with create, update, delete
# and read, search, and query via vital_agent_rest_resource_client

# for changes, these are made first to vital_agent_rest_client
# and upon success, changes make to kgservice via vital_agent_rest_resource_client

# parameter passed to vital_agent_rest_client such that it does not write such changes
# via vital_agent_rest_resource_client to the graph and vector db

# this may be temporary as ideally updates to kgraph would be posted to
# vital-agent-rest and those updates are directly made to kgraph including
# sql, graph, vector dbs and immediately visible to the agent

# however, the purpose of only updating the sql and separately update the
# vector and graph dbs is to allow the agent to "see" the changes its making to rest_resource
# immediately since changes are being made via its client, which may have some caching
# and to not make vital_agent_rest a bottleneck

# if the agent is not directly using drivers (to weaviate, graph db) and
# if vital_agent_rest_resource is updating its cache upon changes made from
# vital_agent_rest then there shouldn't be any caching mis-matches anyway

# such changes should be in the namespace of the current user (account namespace) interacting
# with the agent, so other accounts wouldn't being seeing changes

# changes made to vital_agent_rest_client eventually get replicated into the
# graph and vector dbs acting as indexes of this, and ideally we want to allow that to lag behind
# if the updates are already in the graph and vector db then no net change

# if we're switching to a consolidated kgraph using tidb then sql, graph, vector are
# all in the same service anyway


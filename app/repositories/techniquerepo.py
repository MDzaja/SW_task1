import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getDistinctTechniqueLabels():
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

    # SPARQL query to retrieve data from GraphDB
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    
    SELECT DISTINCT ?technique_label
    WHERE {
        ?technique rdf:type lr:PreparationMethod .
        ?technique rdfs:label ?technique_label .
    }
    ORDER BY ?technique
    """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    techniqueList = []
    for technique in result["results"]["bindings"]:
        techniqueList.append(technique["technique_label"]["value"])

    return techniqueList
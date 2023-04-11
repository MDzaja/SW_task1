import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getDistinctCategoryLabels():
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

    # SPARQL query to retrieve data from GraphDB
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT DISTINCT ?category_label
    WHERE {
        ?category rdf:type skos:Concept .
        ?category skos:prefLabel ?category_label .
    }
    ORDER BY ?category
    """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    categoryList = []
    for category in result["results"]["bindings"]:
        categoryList.append(category["category_label"]["value"])

    return categoryList

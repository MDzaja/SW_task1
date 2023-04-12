import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getDistinctCategoryLabels():
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

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

    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    categoryList = []
    for category in result["results"]["bindings"]:
        categoryList.append(category["category_label"]["value"])

    return categoryList


def getCategories(request):
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """
        PREFIX tp: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX kl: <http://www.w3.org/2004/02/skos/core#>
        PREFIX pref: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?prefLabel
        WHERE {
          ?tag tp:type kl:Concept .
          ?tag pref:prefLabel ?prefLabel.
        } LIMIT 20
        """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(res)
    res = json.loads(res)

    return {"result": res['results']['bindings']}

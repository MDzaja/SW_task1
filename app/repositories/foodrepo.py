import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getDistinctIngredientLabels():
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
    
    SELECT DISTINCT ?ingredient_label
    WHERE {
        ?ingredient rdf:type lr:Food .
        ?ingredient rdfs:label ?ingredient_label .
    }
    ORDER BY ?ingredient
    """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    ingredientList = []
    for ingredient in result["results"]["bindings"]:
        ingredientList.append(ingredient["ingredient_label"]["value"])

    return ingredientList
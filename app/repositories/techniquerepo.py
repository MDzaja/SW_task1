import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getDistinctTechniqueLabels():
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

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

    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    techniqueList = []
    for technique in result["results"]["bindings"]:
        techniqueList.append(technique["technique_label"]["value"])

    return techniqueList


def getTechniques(request):
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    query = """
            PREFIX tp: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX of: <http://linkedrecipes.org/schema/>
            PREFIX pref: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dep: <http://xmlns.com/foaf/0.1/>
            PREFIX des: <http://purl.org/dc/terms/>
            SELECT ?techName ?techImg ?techDescription
            WHERE {
              ?tag a of:PreparationMethod .
              ?tag pref:label ?techName .
              ?tag dep:depiction ?techImg .
              ?tag des:description ?techDescription .
            } LIMIT 20
            """

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(res)
    res = json.loads(res)

    return {"result": res['results']['bindings']}

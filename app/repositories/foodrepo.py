import json
import uuid
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from SPARQLWrapper import SPARQLWrapper, JSON


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


def getIngredients(request):
    query = """
        PREFIX lab: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX lr: <http://linkedrecipes.org/schema/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX dep: <http://xmlns.com/foaf/0.1/>
        PREFIX des: <http://purl.org/dc/terms/>
        SELECT ?food ?label ?depiction ?description
        WHERE {
          ?food a lr:Food .
            ?food lab:label ?label .
            ?food dep:depiction ?depiction .
            ?food des:description ?description .

        }
        ORDER BY ?label 
        LIMIT 20
        """
#     query = """
# PREFIX dc: <http://purl.org/dc/terms/>
# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# SELECT ?label ?description ?food WHERE {
#   ?food dc:description "Pasta spageti" .
#   ?food rdfs:label ?label .
#   ?food a <http://linkedrecipes.org/schema/Food> .
#   ?food dc:description ?description .
# }
# """

    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)

    context = {"result": res['results']['bindings']}
    return context


def addIngredient(request):
        label = request.POST.get('label')
        description = request.POST.get('description')
        myuuid = "<http://data.kasabi.com/dataset/foodista/food/" + str(uuid.uuid4()) + ">"

        query = """
        PREFIX dc: <http://purl.org/dc/terms/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX lr: <http://linkedrecipes.org/schema/>

        INSERT DATA
        {
            %s rdf:type lr:Food ;
                dc:description "%s" ;
                rdfs:label "%s" .
        }
        """ % (myuuid, description, label)

        endpoint = SPARQLWrapper('http://localhost:7200/repositories/WS-foodista/statements')
        endpoint.setMethod('POST')
        endpoint.setRequestMethod('urlencoded')
        endpoint.setQuery(query)
        result = endpoint.query()

def updateIngredientGet(request):
    food_uri = request.GET['food_uri']

    sparql = SPARQLWrapper('http://localhost:7200/repositories/WS-foodista')

    sparql.setQuery(f'''
                PREFIX dc: <http://purl.org/dc/terms/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?label ?description
                WHERE {{
                    <{food_uri}> rdfs:label ?label .
                    <{food_uri}> dc:description ?description .
                }}
            ''')
    sparql.method = 'POST'
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()

    label = result['results']['bindings'][0]['label']['value']
    description = result['results']['bindings'][0]['description']['value']

    return {'food_uri': food_uri, 'label': label, 'description': description}


def updateIngredientPost(request):
    food_uri = request.POST['food_uri']
    label = request.POST['label']
    description = request.POST['description']

    sparql = SPARQLWrapper('http://localhost:7200/repositories/WS-foodista/statements')

    sparql.setQuery(f'''
                PREFIX dc: <http://purl.org/dc/terms/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                DELETE {{ <{food_uri}> rdfs:label ?label . <{food_uri}> dc:description ?description . }}
                INSERT {{ <{food_uri}> rdfs:label "{label}" . <{food_uri}> dc:description "{description}" . }}
                WHERE {{
                    <{food_uri}> rdfs:label ?label .
                    <{food_uri}> dc:description ?description .
                }}
            ''')
    sparql.method = 'POST'
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()


def deleteIngredient(request):
        food_uri = request.POST['food_uri']

        sparql = SPARQLWrapper('http://localhost:7200/repositories/WS-foodista/statements')

        sparql.setQuery(f'''
            PREFIX dc: <http://purl.org/dc/terms/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            DELETE {{ <{food_uri}> rdfs:label ?label . <{food_uri}> dc:description ?description . }}
            WHERE {{
                <{food_uri}> rdfs:label ?label .
                <{food_uri}> dc:description ?description .
            }}
        ''')
        sparql.method = 'POST'
        sparql.setReturnFormat(JSON)
        result = sparql.query().convert()

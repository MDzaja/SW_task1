from django.shortcuts import render
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def vehicle(request):
    # Load the RDF data
    g = Graph()
    g.parse("data_processed.rdf")

    # Define the SPARQL query
    query = """
        PREFIX ds: <https://data.wa.gov/resource/f6w7-q2d2/>
        SELECT ?make ?model ?ev_type ?electric_range
        WHERE {
            ?s ds:make ?make .
            ?s ds:model ?model .
            ?s ds:ev_type ?ev_type .
            ?s ds:electric_range ?electric_range .
        }
    """

    # Execute the SPARQL query
    results = g.query(query)

    # Render the results using a template
    context = {"results": results}
    return render(request, "vehicle_details.html", context)

def recipeTitle(request):
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    # SPARQL query to retrieve data from GraphDB
    query = """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    
    SELECT ?title
    WHERE {
      ?recipe a lr:Recipe ;
              dcterms:title ?title .
    } LIMIT 20
    """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    res = json.loads(res)
    titles = []
    for row in res['results']['bindings']:
        titles.append(row['title']['value'])

    # Render the results using a template
    context = {"titles": titles}
    return render(request, "recipe_titles.html", context)

def home(request):
    return render(request, "home.html")


def ingredients(request):
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    # SPARQL query to retrieve data from GraphDB
    query = """
        PREFIX lab: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX lr: <http://linkedrecipes.org/schema/>
        PREFIX dep: <http://xmlns.com/foaf/0.1/>
        PREFIX des: <http://purl.org/dc/terms/>
        SELECT ?label ?depiction ?description
        WHERE {
          ?food a lr:Food .
            ?food lab:label ?label .
            ?food dep:depiction ?depiction .
            ?food des:description ?description .
                  
        } LIMIT 20
        """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(res)
    res = json.loads(res)
    titles = []

    context = {"result": res['results']['bindings']}
    return render(request, "ingredients.html", context)


def categories(request):
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    # SPARQL query to retrieve data from GraphDB
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

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(res)
    res = json.loads(res)
    titles = []

    context = {"result": res['results']['bindings']}
    return render(request, "categories.html", context)

def techniques(request):
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    repo_name = "WS-foodista"
    client = ApiClient(endpoint=endpoint)
    accessor = GraphDBApi(client)

    # SPARQL query to retrieve data from GraphDB
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

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    res = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    print(res)
    res = json.loads(res)
    titles = []

    context = {"result": res['results']['bindings']}
    return render(request, "techniques.html", context)
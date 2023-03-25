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
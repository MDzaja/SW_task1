from django.shortcuts import render
from rdflib import Graph
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import redirect
import uuid

from app.repositories.categoryrepo import getDistinctCategoryLabels
from app.repositories.foodrepo import getDistinctIngredientLabels
from app.repositories.reciperepo import getCompactRecipes, getCompactRecipes, getRecipeById
from app.repositories.techniquerepo import getDistinctTechniqueLabels


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

def recipes(request):
    selectedCategoryList = request.GET.get('selected_categories', '').split(',')
    selectedTechniqueList = request.GET.get('selected_techniques', '').split(',')
    selectedIngredientList = request.GET.get('selected_ingredients', '').split(',')
    selectedCategoryList = list(filter(None, selectedCategoryList))
    selectedTechniqueList = list(filter(None, selectedTechniqueList))
    selectedIngredientList = list(filter(None, selectedIngredientList))
    searchTitle = request.GET.get('searchTitle', None)
    offset = request.GET.get('offset', 0)

    recipes = getCompactRecipes(offset=offset, limit=30, searchTitle=searchTitle, categoryList=selectedCategoryList,
                                techniqueList=selectedTechniqueList, ingredientList=selectedIngredientList)
    categoryList = getDistinctCategoryLabels()
    techniqueList = getDistinctTechniqueLabels()
    ingredientList = getDistinctIngredientLabels()

    context = {
        "recipe_list": recipes,
        "category_list": categoryList,
        "technique_list": techniqueList,
        "ingredient_list": ingredientList,
        "selected_categories": selectedCategoryList,
        "selected_techniques": selectedTechniqueList,
        "selected_ingredients": selectedIngredientList,
        "offset": offset
    }

    return render(request, "recipes.html", context)

def recipe_details(request, recipe_id):
    recipe = getRecipeById(recipe_id=recipe_id)
    context = {"recipe": recipe}
    return render(request, "recipe_details.html", context)

def home(request):
    return render(request, "home.html")

def ingredients(request):
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

        } LIMIT 20
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
    return render(request, "ingredients.html", context)


def add_ingredient(request):
    if request.method == 'POST':
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

        return redirect("/ingredients/")

    return render(request, "add_ingredient.html")


def update_ingredient(request):
    if request.method == 'POST':
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

        return redirect('/ingredients/')

    else:
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

        return render(request, 'update_ingredient.html', {'food_uri': food_uri, 'label': label, 'description': description})

def delete_ingredient(request):
    if request.method == 'POST':
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

        return redirect('/ingredients/')


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
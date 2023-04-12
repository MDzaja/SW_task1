import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient

def getCompactRecipes(offset=0, limit=20, searchTitle=None, categoryList=None, techniqueList=None, ingredientList=None) -> list:
    # Set up the query parameters
    category_list_string = ", ".join(f'"{category}"' for category in categoryList) if categoryList else None
    technique_list_string = ", ".join(f'"{technique}"' for technique in techniqueList) if techniqueList else None
    search_title = searchTitle.strip() if searchTitle else None
    ingredient_filters = " . ".join([
        f"FILTER EXISTS {{ ?recipe lr:ingredient ?ingredient{i} . " +
        f"?ingredient{i} rdfs:label ?ingredient{i}_name . " +
        f"FILTER (LCASE(?ingredient{i}_name) = LCASE('{ingredientLabel}')) }}"
        for i, ingredientLabel in enumerate(ingredientList)]) if ingredientList else ""

    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

    # SPARQL query to retrieve data from GraphDB
    query = f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?recipe ?title ?servings (GROUP_CONCAT(DISTINCT ?category_label;separator=" ; ") as ?categories) (GROUP_CONCAT(DISTINCT ?ingredient_label;separator=" ; ") as ?ingredients) (GROUP_CONCAT(DISTINCT ?technique_label;separator=" ; ") as ?techniques)
    WHERE {{
      ?recipe rdf:type lr:Recipe .
      ?recipe rdft:title ?title .
      ?recipe lr:servings ?servings .
      
      ?recipe lr:category ?category .
      ?category skos:prefLabel ?category_label .
      
      ?recipe lr:ingredient ?ingredient .
      ?ingredient rdfs:label ?ingredient_label .
      
      ?recipe lr:uses ?technique .
      ?technique rdfs:label ?technique_label .
      
      {ingredient_filters}
      {("FILTER (?category_label in (" + category_list_string + "))") if categoryList else ""}
      {("FILTER (?technique_label in (" + technique_list_string + "))") if techniqueList else ""}
      {("FILTER (REGEX(?title, '.*" + search_title + ".*', 'i'))") if searchTitle else ""}
      
    }}
    GROUP BY ?recipe ?title ?servings
    ORDER BY ?recipe
    OFFSET {offset}
    LIMIT {limit}
    """

    # Execute the query and retrieve the results
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    recipeList = []
    for row in result['results']['bindings']:
        recipeList.append({
            "id": row['recipe']['value'].split("/")[-1],
            "title": row['title']['value'],
            "servings": row['servings']['value'],
            "categories": row['categories']['value'],
            "ingredients": row['ingredients']['value'],
            "techniques": row['techniques']['value']
        })

    return recipeList

def getRecipeById(recipe_id) -> dict:
    recipe = {}
    # Create a connection to the GraphDB repository
    endpoint = "http://localhost:7200"
    client = ApiClient(endpoint=endpoint)
    conn = GraphDBApi(client)
    repo_name = "WS-foodista"

    # get recipe, title, servings
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?recipe ?title ?servings
    WHERE {
      ?recipe rdf:type lr:Recipe .
      ?recipe rdft:title ?title .
      OPTIONAL {?recipe lr:servings ?servings .}
        
      FILTER (?recipe = <http://data.kasabi.com/dataset/foodista/recipe/""" + recipe_id + """>) 
    }
    """
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    for row in result['results']['bindings']:
        recipe['id'] = row['recipe']['value'].split("/")[-1]
        recipe['title'] = row['title']['value']
        recipe['servings'] = row['servings']['value'] if 'servings' in row else None

    # get categories
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?category_label
    WHERE {
      ?recipe rdf:type lr:Recipe .
      
      ?recipe lr:category ?category .
      ?category skos:prefLabel ?category_label .
        
      FILTER (?recipe = <http://data.kasabi.com/dataset/foodista/recipe/""" + recipe_id + """>) 
    }
    """
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    recipe['categories'] = []
    for row in result['results']['bindings']:
        recipe['categories'].append(row['category_label']['value'])

    # get ingredients
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    
    SELECT ?ingredient_label ?ingredient_desc ?ingredient_img
    WHERE {
      ?recipe rdf:type lr:Recipe .
      
      ?recipe lr:ingredient ?ingredient .
      ?ingredient rdfs:label ?ingredient_label .
      ?ingredient rdft:description ?ingredient_desc .
      OPTIONAL {?ingredient foaf:depiction ?ingredient_img .}
        
      FILTER (?recipe = <http://data.kasabi.com/dataset/foodista/recipe/""" + recipe_id + """>) 
    }
    """
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    recipe['ingredients'] = []
    for row in result['results']['bindings']:
        recipe['ingredients'].append({
            "label": row['ingredient_label']['value'],
            "desc": row['ingredient_desc']['value'],
            "img_url": row['ingredient_img']['value'] if 'ingredient_img' in row else None
        })

    # get techniques
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?technique_label ?technique_desc
    WHERE {
      ?recipe rdf:type lr:Recipe .
      
      ?recipe lr:uses ?technique .
      ?technique rdfs:label ?technique_label .
      ?technique rdft:description ?technique_desc .
        
      FILTER (?recipe = <http://data.kasabi.com/dataset/foodista/recipe/""" + recipe_id + """>)  
    }
    """
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    recipe['techniques'] = []
    for row in result['results']['bindings']:
        recipe['techniques'].append({
            "label": row['technique_label']['value'],
            "desc": row['technique_desc']['value']
        })

    # get related recipes
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdft: <http://purl.org/dc/terms/>
    PREFIX lr: <http://linkedrecipes.org/schema/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    
    SELECT ?rel_recipe ?rel_recipe_title
    WHERE {
      ?recipe rdf:type lr:Recipe .
        
      ?recipe rdft:related ?rel_recipe .
      ?rel_recipe rdft:title ?rel_recipe_title .
        
      FILTER (?recipe = <http://data.kasabi.com/dataset/foodista/recipe/""" + recipe_id + """>)
    }
    """
    payload_query = {"query": query}
    result = conn.sparql_select(body=payload_query, repo_name=repo_name)
    result = json.loads(result)
    recipe['related_recipes'] = []
    for row in result['results']['bindings']:
        recipe['related_recipes'].append({
            "id": row['rel_recipe']['value'].split("/")[-1],
            "title": row['rel_recipe_title']['value']
        })

    return recipe

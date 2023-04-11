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
            "recipe": row['recipe']['value'],
            "title": row['title']['value'],
            "servings": row['servings']['value'],
            "categories": row['categories']['value'],
            "ingredients": row['ingredients']['value'],
            "techniques": row['techniques']['value']
        })

    return recipeList

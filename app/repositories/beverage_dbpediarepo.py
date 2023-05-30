from SPARQLWrapper import SPARQLWrapper, JSON
import ssl


def getBeverage(request):
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbp: <http://dbpedia.org/property/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?beverage ?name ?abstract ?type ?ingredientName 
WHERE {
  ?beverage a dbo:Beverage ;
            dbp:name ?name ;
            dbo:abstract ?abstract ;
            dbo:type ?type .
  
  FILTER (LANG(?name) = 'en')
  FILTER (LANG(?abstract) = 'en')
  
  OPTIONAL { ?beverage dbo:ingredientName ?ingredientName }
}
LIMIT 20

    """

    sparql.setQuery(query)
    results = sparql.query().convert()

    context = {"result": results['results']['bindings']}
    return context
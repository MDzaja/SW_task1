from SPARQLWrapper import SPARQLWrapper, JSON
import ssl


def getFood(request):
    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)

    query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?foodLabel ?foodDescription
    WHERE {
      ?food rdf:type dbo:Food ;
            rdfs:label ?foodLabel ;
            dbo:abstract ?foodDescription .

      FILTER (LANG(?foodLabel) = 'en')  # Filter results to English labels
      FILTER (LANG(?foodDescription) = 'en')  # Filter results to English descriptions
    }
    LIMIT 10
    """

    sparql.setQuery(query)
    results = sparql.query().convert()

    context = {"result": results['results']['bindings']}
    return context
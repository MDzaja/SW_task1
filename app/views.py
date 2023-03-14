from django.shortcuts import render
from rdflib import Graph


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

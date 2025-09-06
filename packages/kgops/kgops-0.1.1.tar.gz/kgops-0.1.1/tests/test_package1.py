
from kgops import Resource, KGOps


kg = KGOps(
    backend='networkx',
)

graph = kg.create_graph(
    name='test_graph',
    description='A test graph'
)

person = Resource(
    labels={"person"},
    properties={
        "name": "John Doe",
        "age": 30
    }
)

company = Resource(
    labels={"Organization", "Company"},
    properties={
        "name": "TechCorp",
        "industry": "Technology",
        "founded": 2010
    }
)

kg.add_resource(person)
kg.add_resource(company)

kg.add_edge(person, company, "WORKS_AT", start_date="2023-01-01")

neighbours = kg.query('neighbors', resource_id=person.id)

print("Neighbours found:", len(neighbours) , "entities")


stats = kg.stats()


print("Graph stats:", stats)

kg.save_graph("test_graph.json")
# The Simpsons in RDF
This is an example file modeling the Simpsons Family in RDF.
It was originally taken from

http://sws.ifi.uio.no/inf3580/v15/oblig/3/simpsons.ttl

where it is part of an assignment:

https://www.uio.no/studier/emner/matnat/ifi/INF3580/v17/undervisningsmateriale/oblig_4.pdf

I have slightly adopted it and moved it to the `<https://simpsons.example.org/>` namespace.

The simpsons graph is also included in the [JekyllRDF tutorial](https://github.com/white-gecko/JekyllRDF-Tutorial): https://github.com/white-gecko/JekyllRDF-Tutorial/blob/master/_data/graph.ttl ([JekyllRDF](https://github.com/AKSW/jekyll-rdf))

## Usage in Python

To use it in python do:

```sh
pip install simpsons-rdf
```

or

```sh
poetry add simpsons-rdf
```

use it like any other [RDFLib](https://rdflib.dev/) [Graph](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html#rdflib.graph.Graph) object.

```python
from simpsons import simpsons, SIM, FAM

print({p: o for _, p, o in simpsons.graph.triples((SIM.Homer, None, None))})
print([spouse for _, _, spouse in simpsons.graph.triples((SIM.Homer, FAM.hasSpouse, None))])
print(simpsons.graph.serialize(format="turtle"))
```

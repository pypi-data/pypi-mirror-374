from abc import ABC

import pandas as pd
import rdflib

from gldb.query.query import Query, QueryResult
from gldb.stores import RDFStore, RemoteSparqlStore


def parse_literal(literal):
    if isinstance(literal, rdflib.Literal):
        return literal.value
    if isinstance(literal, rdflib.URIRef):
        return str(literal)
    return literal


def sparql_result_to_df(bindings):
    return pd.DataFrame([{str(k): parse_literal(v) for k, v in binding.items()} for binding in bindings])


class MetadataStoreQuery(Query, ABC):
    """RDF Store Query interface."""


class SparqlQuery(MetadataStoreQuery):
    """A SPARQL query interface for RDF stores."""

    def execute(self, store: RDFStore, *args, **kwargs):
        return QueryResult(
            query=self,
            data=sparql_result_to_df(store.graph.query(self.query, *args, **kwargs).bindings),
            description=self.description
        )


class RemoteSparqlQuery(MetadataStoreQuery):

    def execute(self, store: RemoteSparqlStore, *args, **kwargs) -> QueryResult:
        sparql = store.wrapper
        sparql.setQuery(self.query)

        results = sparql.queryAndConvert()

        return QueryResult(
            query=self,
            data=results,
            description=self.description
        )

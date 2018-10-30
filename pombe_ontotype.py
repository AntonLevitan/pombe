import goatools.associations
import goatools.obo_parser
import pandas as pd
import collections

from constants import DATA_DIRECTORY, GENEONTOLOGY_FILENAME, POMBE_FILENAME

def read_go():

    ontology = goatools.obo_parser.GODag(DATA_DIRECTORY + GENEONTOLOGY_FILENAME, optional_attrs=["relationship"], load_obsolete=True)

    for term in ontology.values():
        term.parents.update(getattr(term, "relationship", { "part_of": set() }).get("part_of", set()))

    return ontology


def read_gene_ass():

    gene_ass = goatools.associations.read_gaf(DATA_DIRECTORY + POMBE_FILENAME)
    
    return gene_ass

def read_interactions():
    
    interactions_filename = DATA_DIRECTORY + "gene_interactions.csv"
    interactions_data = pd.read_table(interactions_filename)

    return interactions_data

def read_data():

    ontology = read_go()
    associations = read_gene_ass()
    training_data = read_interactions()

    return ontology, associations, training_data

x = read_data()
print(x[2].head())

import goatools.associations
import goatools.obo_parser
import pandas as pd
import collections

from constants import DATA_DIRECTORY, GENEONTOLOGY_FILENAME, POMBE_FILENAME, COMBINED_FILENAME, GENE_INTERACTIONS

INDEX_COLUMNS = ['Gene A', 'Gene B']

def read_go():

    ontology = goatools.obo_parser.GODag(DATA_DIRECTORY + GENEONTOLOGY_FILENAME, optional_attrs=["relationship"], load_obsolete=True)

    for term in ontology.values():
        term.parents.update(getattr(term, "relationship", { "part_of": set() }).get("part_of", set()))

    return ontology


def read_gene_ass():

    gene_ass = goatools.associations.read_gaf(DATA_DIRECTORY + POMBE_FILENAME)
    
    return gene_ass


def read_interactions():
    
    interactions_filename = DATA_DIRECTORY + GENE_INTERACTIONS
    interactions_data = pd.read_csv(interactions_filename, index_col=INDEX_COLUMNS)
    interactions_data.to_csv('GI_indexed.csv')

    return interactions_data


def read_data():

    ontology = read_go()
    associations = read_gene_ass()
    training_data = read_interactions()

    return ontology, associations, training_data

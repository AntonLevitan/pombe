import collections
import goatools.associations
import numpy
import pandas
import sklearn.feature_extraction


def filter_association(ontology, association, min_genes, max_genes):

    association = goatools.associations.get_assc_pruned(association, min_genes, max_genes)[0]

    reverse_association = goatools.associations.get_b2aset(association)
    removed_ids = set()

    for (go_id, geneids) in reverse_association.items():
        for parent in ontology[go_id].parents:
            if parent.id in reverse_association and len(reverse_association[parent.id]) == len(geneids):
                removed_ids.add(parent.id)

    for go_id in removed_ids:
        del reverse_association[go_id]

    return goatools.associations.get_b2aset(reverse_association)


def generate_gene_ontotypes(association):
    
    geneid_ontotypes = collections.defaultdict(collections.Counter, { geneid: collections.Counter(go_ids) for (geneid, go_ids) in association.items() })

    return geneid_ontotypes

def generate_ontotype(genotype, gene_ontotypes, training_ids=None):
    
    ontotype_data = [sum([gene_ontotypes.get(gene, collections.Counter()) for gene in genes], collections.Counter()) for genes in genotype.index]

    vectorizer = sklearn.feature_extraction.DictVectorizer(dtype=numpy.uint8, sparse=False)
    ontotype = vectorizer.fit_transform(ontotype_data)
    go_ids = vectorizer.get_feature_names()

    return pandas.DataFrame(ontotype, index=genotype.index, columns=go_ids).reindex(columns=training_ids, fill_value=numpy.uint8(0))

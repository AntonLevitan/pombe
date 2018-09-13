import argparse
import json
import pandas
import sklearn.ensemble

from download_data import download_data
from read_data import read_data
from generate_ontotype import filter_association, generate_gene_ontotypes, generate_ontotype
from generate_phenotype import score_training_data, train_prediction_model, generate_phenotype
from cross_validate import cross_validate

SPECIES_INFO_FILENAME = "species.json"

DOWNLOAD_FLAG = "--dl"
CV_FLAG = "--cv"
MIN_FLAG = "--min"
MAX_FLAG = "--max"
SPECIES_FLAG = "-s"
ONTOTYPE_FLAG = "-o"

def read_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(DOWNLOAD_FLAG, dest="force_dl", action="store_true")
    parser.add_argument(SPECIES_FLAG, dest="species", default="S_cerevisiae")
    parser.add_argument(MIN_FLAG, dest="min_genes")
    parser.add_argument(MAX_FLAG, dest="max_genes")

    parser.add_argument(CV_FLAG, dest="crossval_filename", nargs='?', const="crossval.png")
    parser.add_argument(ONTOTYPE_FLAG, dest="ontotype_filename", nargs='?', const="ontotype.txt")

    parser.add_argument("genotype_filename", default="genotype.txt", nargs='?')
    parser.add_argument("phenotype_filename", default="phenotype.txt", nargs='?')

    return parser.parse_args()

def genotype_to_phenotype():
    settings = read_arguments()

    with open(SPECIES_INFO_FILENAME) as species_info_file:
        species_info = json.load(species_info_file)

    download_data(species_info, settings.force_dl)
    ontology, association, alias_map, training_data = read_data(settings.species, species_info)

    ontology.update_association(association)
    filtered_association = filter_association(association, ontology, settings.min_genes, settings.max_genes)
    gene_ontotypes = generate_gene_ontotypes(filtered_association, alias_map)

    training_scores = score_training_data(settings.species, training_data)
    training_ontotype = generate_ontotype(training_scores, gene_ontotypes)
    classifier = sklearn.ensemble.RandomForestClassifier(n_jobs=-1)

    if settings.crossval_filename:
        cross_validate(training_ontotype, training_scores, classifier, settings.crossval_filename)
    else:
        genotype = pandas.read_table(settings.genotype_filename, header=None, delim_whitespace=True, dtype=str).set_index([0,1]).rename_axis([None, None])
        ontotype = generate_ontotype(genotype, gene_ontotypes, training_ontotype.columns)

        if settings.ontotype_filename:
            ontotype.to_csv(settings.ontotype_filename, sep='\t')

        model = train_prediction_model(training_ontotype, training_scores, classifier)
        phenotype = generate_phenotype(ontotype, model)
        phenotype.to_csv(settings.phenotype_filename, sep='\t', header=False)

if __name__ == "__main__":
    genotype_to_phenotype()

import argparse
import json
import pandas

from download_data import download_data
from read_data import read_data
from generate_ontotype import filter_association, generate_gene_ontotypes, generate_ontotype
from generate_phenotype import score_training_data, train_prediction_model, generate_phenotype, score_training_data_reg
from cross_validate import cross_validate, regression_cv

SPECIES_INFO_FILENAME = "species.json"

DOWNLOAD_FLAG = "--dl"
CV_FLAG = "--cv"
CVR_FLAG = "--cvr"
MIN_FLAG = "--min"
MAX_FLAG = "--max"
SPECIES_FLAG = "-s"
ONTOTYPE_FLAG = "-o"


def read_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(DOWNLOAD_FLAG, dest="force_dl", action="store_true")
    parser.add_argument(CV_FLAG, dest="crossval", action="store_true")
    parser.add_argument(CVR_FLAG, dest="crossvalreg", action="store_true")
    parser.add_argument(MIN_FLAG, dest="min_genes")
    parser.add_argument(MAX_FLAG, dest="max_genes")
    parser.add_argument(SPECIES_FLAG, dest="species", default="S_cerevisiae")
    parser.add_argument(ONTOTYPE_FLAG, dest="ontotype_filename", nargs='?', const="all_sc_ontotype.txt")

    parser.add_argument("genotype_filename", default="all_sc_genotype.txt", nargs='?')
    parser.add_argument("phenotype_filename", default="all_sc_phenotype.txt", nargs='?')

    return parser.parse_args()


def genotype_to_phenotype():
    settings = read_arguments()

    with open(SPECIES_INFO_FILENAME) as species_info_file:
        species_info = json.load(species_info_file)

    download_data(species_info, settings.force_dl)
    ontology, associations, alias_maps, training_data = read_data(species_info)

    gene_ontotypes = {}
    training_ontotypes = {}
    prediction_models = {}

    for species in species_info:
        ontology.update_association(associations[species])
        filtered_association = filter_association(ontology, associations[species], settings.min_genes,
                                                  settings.max_genes)
        gene_ontotypes[species] = generate_gene_ontotypes(filtered_association, alias_maps[species])

        if training_data[species] is not None:
            training_scores = score_training_data(training_data[species])
            training_ontotypes[species] = generate_ontotype(training_scores, gene_ontotypes[species])
            prediction_models[species] = train_prediction_model(training_ontotypes[species], training_scores)
            # training_scores_reg = score_training_data_reg(training_data[species])

            if settings.crossval:
                cross_validate(species, training_ontotypes[species], training_scores)

            if settings.crossvalreg:
                regression_file = open('new_sc_regression2.txt', "w+")
                training_scores_reg = score_training_data_reg(training_data[species])
                training_ontotypes[species] = generate_ontotype(training_scores_reg, gene_ontotypes[species])
                regression_cv(training_ontotypes[species], training_scores_reg, regression_file)
                regression_file.close()

    genotype = pandas.read_table(settings.genotype_filename, header=None,
                                 delim_whitespace=True, dtype=str).set_index([0, 1]).rename_axis([None, None])

    ontotype = generate_ontotype(genotype, gene_ontotypes[settings.species],
                                 training_ontotypes[settings.species].columns)

    if settings.ontotype_filename is not None:
        ontotype.to_csv(settings.ontotype_filename, sep='\t')

    phenotype = generate_phenotype(ontotype, prediction_models[settings.species])
    phenotype.to_csv(settings.phenotype_filename, sep='\t', header=False)


if __name__ == "__main__":
    genotype_to_phenotype()

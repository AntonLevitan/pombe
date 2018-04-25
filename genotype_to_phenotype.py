import getopt
import json
import pandas
import sys

import settings

from download_data import download_data
from read_data import read_data
from generate_ontotype import filter_association, generate_gene_ontotypes, generate_ontotype
from generate_phenotype import score_training_data, train_prediction_model, generate_phenotype
from cross_validate import cross_validate

SPECIES_INFO_FILENAME = "species.json"

DOWNLOAD_FLAG = "dl"
CV_FLAG = "cv"
MIN_FLAG = "min"
MAX_FLAG = "max"
SPECIES_FLAG = 's'
ONTOTYPE_FLAG = 'o'

def read_arguments():
    opts, args = getopt.getopt(sys.argv[1:], SPECIES_FLAG + ':' + ONTOTYPE_FLAG + ':', [DOWNLOAD_FLAG, MIN_FLAG + '=', MAX_FLAG + '=', CV_FLAG])

    for opt, arg in opts:
        if opt == "--" + DOWNLOAD_FLAG:
            settings.download = True
        elif opt == "--" + MIN_FLAG:
            settings.min_genes = int(arg)
        elif opt == "--" + MAX_FLAG:
            settings.max_genes = int(arg)
        elif opt == '-' + SPECIES_FLAG:
            settings.species = arg
        elif opt =="--" + CV_FLAG:
            settings.crossval = True
        elif opt == '-' + ONTOTYPE_FLAG:
            settings.ontotype_filename = arg

    if len(args) > 0:
        settings.genotype_filename = args[0]
    if len(args) > 1:
        settings.phenotype_filename = args[1]

def genotype_to_phenotype():
    read_arguments()

    with open(SPECIES_INFO_FILENAME) as species_info_file:
        species_info = json.load(species_info_file)

    download_data(species_info)
    ontology, associations, alias_maps, training_data = read_data(species_info)

    gene_ontotypes = {}
    training_ontotypes = {}
    prediction_models = {}

    for species in species_info:
        ontology.update_association(associations[species])
        filtered_association = filter_association(ontology, associations[species])
        gene_ontotypes[species] = generate_gene_ontotypes(filtered_association, alias_maps[species])

        if training_data[species] is not None:
            training_scores = score_training_data(training_data[species])
            training_ontotypes[species] = generate_ontotype(training_scores, gene_ontotypes[species])
            prediction_models[species] = train_prediction_model(training_ontotypes[species], training_scores)

            if settings.crossval:
                cross_validate(species, training_ontotypes[species], training_scores)

    genotype = pandas.read_table(settings.genotype_filename, header=None, delim_whitespace=True, dtype=str).set_index([0,1]).rename_axis([None, None])
    ontotype = generate_ontotype(genotype, gene_ontotypes[settings.species], training_ontotypes[settings.species].columns)

    if settings.ontotype_filename is not None:
        ontotype.to_csv(settings.ontotype_filename, sep='\t')

    phenotype = generate_phenotype(ontotype, prediction_models[settings.species])
    phenotype.to_csv(settings.phenotype_filename, sep='\t', header=False)

if __name__ == "__main__":
    genotype_to_phenotype()

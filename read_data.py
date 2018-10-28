import collections
import goatools.associations
import goatools.obo_parser
import pandas

from constants import DATA_DIRECTORY, GENEINFO_FILE_SUFFIX, GENEONTOLOGY_FILENAME, GENE2GO_FILENAME, COSTANZO_FILENAME, TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN

GENEINFO_GENEID_COLUMN = "GeneID"
GENEINFO_COLUMNS = [GENEINFO_GENEID_COLUMN, "Symbol", "LocusTag", "Synonyms"]

TRAINING_INDEX_COLUMNS = ["Query", "Array"]
TRAINING_COLUMNS = TRAINING_INDEX_COLUMNS + [TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN]


def read_go():
    ontology = goatools.obo_parser.GODag(DATA_DIRECTORY + GENEONTOLOGY_FILENAME, optional_attrs=["relationship"], load_obsolete=True)

    for term in ontology.values():
        term.parents.update(getattr(term, "relationship", { "part_of": set() }).get("part_of", set()))

    return ontology


def read_gene2go(species_info):
    tax_ids = [species["taxonomy_id"] for species in species_info.values()]
    associations = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(set)))

    goatools.associations.read_ncbi_gene2go(DATA_DIRECTORY + GENE2GO_FILENAME, tax_ids, taxid2asscs=associations)

    return {species_id: associations[species["taxonomy_id"]]["GeneID2GOs"] for (species_id, species) in species_info.items()}


def read_geneinfo(species):
    geneinfo_filename = DATA_DIRECTORY + species["geneinfo_name"] + GENEINFO_FILE_SUFFIX
    geneinfo_data = pandas.read_table(geneinfo_filename, usecols=GENEINFO_COLUMNS, index_col=GENEINFO_GENEID_COLUMN)

    alias_map = {}

    for (geneid, symbol, locus_tag, synonyms) in geneinfo_data.itertuples():
        alias_map[str(geneid)] = geneid
        alias_map[symbol] = geneid
        if locus_tag != '-':
            alias_map[locus_tag] = geneid
        if synonyms != '-':
            for synonym in str(synonyms).split('|'):
                alias_map[synonym] = geneid

    return alias_map


def read_costanzo():
    costanzo_filename = DATA_DIRECTORY + COSTANZO_FILENAME
    costanzo_data = pandas.read_table(costanzo_filename, header=None, usecols=[0,2,4,6], names=TRAINING_COLUMNS, index_col=TRAINING_INDEX_COLUMNS)

    return costanzo_data.rename(index=lambda gene: gene.split("_")[0], level=0).sort_index()


def read_data(species_info):
    ontology = read_go()
    associations = read_gene2go(species_info)
    alias_maps = {}

    for (species_id, species) in species_info.items():
        alias_maps[species_id] = read_geneinfo(species)

    training_data = collections.defaultdict(lambda: None)
    training_data["S_cerevisiae"] = read_costanzo()

    return ontology, associations, alias_maps, training_data

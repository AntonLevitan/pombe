import gzip
import os
import StringIO
import urllib
import urllib2

from constants import DATA_DIRECTORY, GENEONTOLOGY_BASE_FILENAME, GENE2GO_BASE_FILENAME, GENEINFO_FILE_SUFFIX, COSTANZO_BASE_FILENAME

GENEINFO_URL_PREFIX = "ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/"
GENEONTOLOGY_URL_PREFIX = "http://geneontology.org/ontology/"
GENE2GO_URL_PREFIX = "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/"
COSTANZO_URL_PREFIX = "http://boonelab.ccbr.utoronto.ca/supplement/costanzo2009/"

GZIP_FILE_SUFFIX = ".gz"

def download_go(force_dl):
    go_url = GENEONTOLOGY_URL_PREFIX + GENEONTOLOGY_BASE_FILENAME
    go_filename = DATA_DIRECTORY + GENEONTOLOGY_BASE_FILENAME

    if force_dl or not os.path.exists(go_filename):
        urllib.urlretrieve(go_url, go_filename)

def download_gene2go(force_dl):
    gene2go_url = GENE2GO_URL_PREFIX + GENE2GO_BASE_FILENAME + GZIP_FILE_SUFFIX
    gene2go_filename = DATA_DIRECTORY + GENE2GO_BASE_FILENAME

    if force_dl or not os.path.exists(gene2go_filename):
        download_gzipped_url(gene2go_url, gene2go_filename)

def download_geneinfo(species, force_dl):
    geneinfo_base_filename = species["geneinfo_name"] + GENEINFO_FILE_SUFFIX
    geneinfo_url = GENEINFO_URL_PREFIX + species["geneinfo_dir"] + '/' + geneinfo_base_filename + GZIP_FILE_SUFFIX
    geneinfo_filename = DATA_DIRECTORY + geneinfo_base_filename

    if force_dl or not os.path.exists(geneinfo_filename):
        download_gzipped_url(geneinfo_url, geneinfo_filename)

def download_costanzo(force_dl):
    costanzo_url = COSTANZO_URL_PREFIX + COSTANZO_BASE_FILENAME + GZIP_FILE_SUFFIX
    costanzo_filename = DATA_DIRECTORY + COSTANZO_BASE_FILENAME

    if force_dl or not os.path.exists(costanzo_filename):
        download_gzipped_url(costanzo_url, costanzo_filename)

def download_gzipped_url(url, filename):
    download = urllib2.urlopen(url)
    zipped = StringIO.StringIO(download.read())
    unzipped = gzip.GzipFile(fileobj=zipped)

    with open(filename, 'w') as file:
        file.write(unzipped.read())

    unzipped.close()
    zipped.close()
    download.close()

def download_data(species_info, force_dl):
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    download_go(force_dl)
    download_gene2go(force_dl)

    for species in species_info.values():
        download_geneinfo(species, force_dl)

    download_costanzo(force_dl)

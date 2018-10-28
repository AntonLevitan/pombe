import gzip
import os

try:
    import StringIO
except:
    from io import BytesIO

import urllib

try:
    from urllib.request import urlretrieve, urlopen
except:
    pass

try:
    import urllib2
except:
    pass

import zipfile

from constants import DATA_DIRECTORY, GENEONTOLOGY_FILENAME, GENE2GO_FILENAME, GENEINFO_FILE_SUFFIX, COSTANZO_FILENAME, POMBE_SUFFIX, POMBE_FILENAME


GENEINFO_URL_PREFIX = "ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/"
GENEONTOLOGY_URL_PREFIX = "http://geneontology.org/ontology/"
GENE2GO_URL_PREFIX = "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/"
COSTANZO_URL_PREFIX = "http://boonelab.ccbr.utoronto.ca/supplement/costanzo2009/"

GENE_ASS_URL_PREFIX = "http://geneontology.org/gene-associations/" 

GZIP_FILE_SUFFIX = ".gz"


def download_gzip(url, filename):
    try:
        download = urlopen(url)
    except:        
        download = urllib2.urlopen(url)
    try:
        zipped = StringIO.StringIO(download.read())
    except:
        zipped = BytesIO(download.read())

    unzipped = gzip.GzipFile(fileobj=zipped)

    with open(DATA_DIRECTORY + filename, 'wb') as file:
        file.write(unzipped.read())

    unzipped.close()
    zipped.close()
    download.close()


def download_zip(url, filename):
    try:
        download = urlopen(url)
    except:        
        download = urllib2.urlopen(url)

    try:    
        zipped = StringIO.StringIO(download.read())
    except:
        zipped = BytesIO(download.read())

    with zipfile.ZipFile(zipped) as unzipped:
        unzipped.extract(filename, DATA_DIRECTORY)

    zipped.close()
    download.close()


def download_raw(url, filename):
    try:
        urlretrieve(url, DATA_DIRECTORY + filename)
    except:
        urllib.urlretrieve(url, DATA_DIRECTORY + filename)
        


def download_file(url, filename, compression, force_dl):
    if force_dl or not os.path.exists(DATA_DIRECTORY + filename):
        if compression == "gzip":
            download_gzip(url, filename)
        elif compression == "zip":
            download_zip(url, filename)
        elif compression == "raw":
            download_raw(url, filename)


def download_geneinfo(species, force_dl):
    geneinfo_filename = species["geneinfo_name"] + GENEINFO_FILE_SUFFIX
    geneinfo_url = GENEINFO_URL_PREFIX + species["geneinfo_dir"] + '/' + geneinfo_filename + GZIP_FILE_SUFFIX

    download_file(geneinfo_url, geneinfo_filename, "gzip", force_dl)


def download_data(species_info, force_dl):
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)

    download_file(GENEONTOLOGY_URL_PREFIX + GENEONTOLOGY_FILENAME, GENEONTOLOGY_FILENAME, "raw", force_dl)
    download_file(GENE2GO_URL_PREFIX + GENE2GO_FILENAME + GZIP_FILE_SUFFIX, GENE2GO_FILENAME, "gzip", force_dl)
    download_file(GENE_ASS_URL_PREFIX + POMBE_SUFFIX + GZIP_FILE_SUFFIX, POMBE_FILENAME, "gzip", force_dl)

    for species in species_info.values():
        download_geneinfo(species, force_dl)

    download_file(COSTANZO_URL_PREFIX + COSTANZO_FILENAME + GZIP_FILE_SUFFIX, COSTANZO_FILENAME, "gzip", force_dl)

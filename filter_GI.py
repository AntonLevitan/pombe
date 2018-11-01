import pandas
import sklearn.ensemble
import numpy as np

from constants import TRAINING_SCORE_COLUMN

PHENOTYPE_COLUMN = "Phenotype"
INDEX_COLUMNS = ['Gene A', 'Gene B']

SCORE_THRESHOLD = 1

data = pandas.read_csv('GI_indexed.csv', index_col=INDEX_COLUMNS)


def score_training_data(training_data):

    negatives = training_data[training_data[TRAINING_SCORE_COLUMN] <= -SCORE_THRESHOLD]
    positives = training_data[training_data[TRAINING_SCORE_COLUMN] >= SCORE_THRESHOLD]
    no_interaction = training_data.drop(negatives.index | positives.index)
    training_scores = pandas.concat([negatives, positives]).sort_index().drop([TRAINING_SCORE_COLUMN], axis=1)
    training_scores[PHENOTYPE_COLUMN] = 0
    training_scores.loc[positives.index, PHENOTYPE_COLUMN] = 1
  
    training_scores.to_csv('filtered_GI.csv')

if __name__ == "__main__":
    score_training_data(data)

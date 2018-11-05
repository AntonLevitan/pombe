import pandas
import sklearn.ensemble
import numpy as np

from constants import TRAINING_SCORE_COLUMN, SIMILARITY_SCORE_COLUMN


PHENOTYPE_COLUMN = "Phenotype"
INDEX_COLUMNS = ['Gene A', 'Gene B']

SCORE_THRESHOLD = 0.7
SIMILARITY_THRESHOLD = 0.002

data = pandas.read_csv('GI_indexed.csv', index_col=INDEX_COLUMNS)


def score_training_data(training_data):

    negatives = training_data[(training_data[TRAINING_SCORE_COLUMN] <= -SCORE_THRESHOLD) & (training_data[SIMILARITY_SCORE_COLUMN] >= SIMILARITY_THRESHOLD)]
    positives = training_data[(training_data[TRAINING_SCORE_COLUMN] >= SCORE_THRESHOLD) & (training_data[SIMILARITY_SCORE_COLUMN] >= SIMILARITY_THRESHOLD)]
    no_interaction = training_data.drop(negatives.index | positives.index).sample(n=len(negatives))
    training_scores = pandas.concat([negatives, no_interaction]).sort_index().drop([TRAINING_SCORE_COLUMN, SIMILARITY_SCORE_COLUMN], axis=1)
    training_scores[PHENOTYPE_COLUMN] = 0
    training_scores.loc[negatives.index, PHENOTYPE_COLUMN] = 1
  
    training_scores.to_csv('filtered_GI.csv')


if __name__ == "__main__":
    score_training_data(data)

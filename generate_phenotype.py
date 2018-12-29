import pandas
import sklearn.ensemble
import numpy as np

from constants import TRAINING_SCORE_COLUMN, SIMILARITY_SCORE_COLUMN

PHENOTYPE_COLUMN = "Phenotype"

SCORE_THRESHOLD = 2.3
SIMILARITY_THRESHOLD = 0


def score_training_data(training_data):

    negatives = training_data[training_data[TRAINING_SCORE_COLUMN] <= -SCORE_THRESHOLD]
    positives = training_data[training_data[TRAINING_SCORE_COLUMN] >= SCORE_THRESHOLD]
    no_interaction = training_data.drop(negatives.index | positives.index).sample(n=len(negatives))
    training_scores = pandas.concat([negatives, no_interaction]).sort_index().drop(TRAINING_SCORE_COLUMN, axis=1)
    training_scores[PHENOTYPE_COLUMN] = 0
    training_scores.loc[negatives.index, PHENOTYPE_COLUMN] = 1

    return training_scores


def train_prediction_model(training_ontotype, training_scores):
    return sklearn.ensemble.RandomForestClassifier(n_jobs=-1, random_state=15).fit(training_ontotype, training_scores.values.ravel())


def generate_phenotype(ontotype, model):
    phenotype = model.predict_proba(ontotype)[:, 1]

    return pandas.DataFrame(phenotype, index=ontotype.index, columns=[PHENOTYPE_COLUMN])

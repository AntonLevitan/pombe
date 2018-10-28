import pandas
import sklearn.ensemble

from constants import TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN

PHENOTYPE_COLUMN = "Phenotype"

SCORE_THRESHOLD = 0.08
PVALUE_THRESHOLD = 0.05


def score_training_data(training_data):
    negatives = training_data.loc[(training_data[TRAINING_SCORE_COLUMN] <= -SCORE_THRESHOLD) & (training_data[TRAINING_PVALUE_COLUMN] <= PVALUE_THRESHOLD)]
    positives = training_data.loc[(training_data[TRAINING_SCORE_COLUMN] >= SCORE_THRESHOLD) & (training_data[TRAINING_PVALUE_COLUMN] <= PVALUE_THRESHOLD)]
    no_interaction = training_data.drop(negatives.index | positives.index).sample(n=len(negatives))

    training_scores = pandas.concat([negatives, no_interaction]).sort_index().drop([TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN], axis=1)
    training_scores[PHENOTYPE_COLUMN] = 0
    training_scores.loc[negatives.index, PHENOTYPE_COLUMN] = 1

    return training_scores


def train_prediction_model(training_ontotype, training_scores):
    return sklearn.ensemble.RandomForestClassifier(n_jobs=-1).fit(training_ontotype, training_scores.values.ravel())


def generate_phenotype(ontotype, model):
    phenotype = model.predict_proba(ontotype)[:,1]

    return pandas.DataFrame(phenotype, index=ontotype.index, columns=[PHENOTYPE_COLUMN])

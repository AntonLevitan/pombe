import pandas
import sklearn.linear_model

from constants import TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN

PHENOTYPE_COLUMN = "Phenotype"

SCORE_THRESHOLD = -0.08
PVALUE_THRESHOLD = 0.05

def score_training_data(training_data):
    training_data[PHENOTYPE_COLUMN] = 0
    negatives = (training_data[TRAINING_SCORE_COLUMN] <= SCORE_THRESHOLD) & (training_data[TRAINING_PVALUE_COLUMN] <= PVALUE_THRESHOLD)
    training_data.loc[negatives, PHENOTYPE_COLUMN] = 1
    training_data.drop([TRAINING_SCORE_COLUMN, TRAINING_PVALUE_COLUMN], axis=1, inplace=True)

def train_prediction_model(training_ontotype, training_data):
    return sklearn.linear_model.LogisticRegression().fit(training_ontotype, training_data.values.ravel())

def generate_phenotype(ontotype, model):
    phenotype = model.predict_proba(ontotype)[:,1]

    return pandas.DataFrame(phenotype, index=ontotype.index, columns=[PHENOTYPE_COLUMN])

import pandas

from constants import COSTANZO_SCORE_COLUMN, COSTANZO_PVALUE_COLUMN

PHENOTYPE_COLUMN = "Phenotype"

SCORE_THRESHOLD = 0.08
PVALUE_THRESHOLD = 0.05

def score_training_data(species, training_data):
    training_scores = None

    if species == "S_cerevisiae":
        training_scores = score_costanzo_data(training_data)

    return training_scores

def score_costanzo_data(costanzo):
    negatives = costanzo.loc[(costanzo[COSTANZO_SCORE_COLUMN] <= -SCORE_THRESHOLD) & (costanzo[COSTANZO_PVALUE_COLUMN] <= PVALUE_THRESHOLD)]
    positives = costanzo.loc[(costanzo[COSTANZO_SCORE_COLUMN] >= SCORE_THRESHOLD) & (costanzo[COSTANZO_PVALUE_COLUMN] <= PVALUE_THRESHOLD)]
    no_interaction = costanzo.drop(negatives.index | positives.index).sample(n=len(negatives))

    training_scores = pandas.concat([negatives, no_interaction]).sort_index().drop([COSTANZO_SCORE_COLUMN, COSTANZO_PVALUE_COLUMN], axis=1)
    training_scores[PHENOTYPE_COLUMN] = 0
    training_scores.loc[negatives.index, PHENOTYPE_COLUMN] = 1

    return training_scores

def train_prediction_model(training_ontotype, training_scores, classifier):
    return classifier.fit(training_ontotype, training_scores.values.ravel())

def generate_phenotype(ontotype, model):
    phenotype = model.predict_proba(ontotype)[:,1]

    return pandas.DataFrame(phenotype, index=ontotype.index, columns=[PHENOTYPE_COLUMN])

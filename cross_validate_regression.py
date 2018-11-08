import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import StratifiedKFold, cross_val_predict


def regression(training_ontotype, training_scores):
    X = training_ontotype.values
    y = training_scores.values.ravel()
    cv = StratifiedKFold(n_splits=5, random_state=15)
    regressor = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=15)
    probas_ = sklearn.model_selection.cross_val_predict(regressor, X, y, cv=cv, n_jobs=6)
    
    pearson = []

    for train, test in cv.split(X, y):
        regressor.fit(X[train], y[train])
        cv_x = pearsonr(y[test], probas_[test])
        pearson.append(cv_x[0])

    pearson.append(sum(pearson)/len(pearson))
    f_pearson = open("pearson.txt", "w+")
    f_pearson.write(str(pearson))
    f_pearson.close()

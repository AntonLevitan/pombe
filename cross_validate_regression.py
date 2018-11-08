import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_predict


def regression(training_ontotype, training_scores):
    X = training_ontotype.values
    y = training_scores.values.ravel()
    # X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.7, random_state=15)
    cv = StratifiedKFold(n_splits=5, random_state=15)
    regressor = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=15)
    probas_ = sklearn.model_selection.cross_val_predict(regressor, X, y, cv=cv, n_jobs=6)
    
    pearson = []

    for train, test in cv.split(X, y):
        regressor.fit(X[train], y[train])
        cv_x = pearsonr(y[test], probas_[test])
        pearson.append(cv_x[0])

    pearson.append(sum(pearson)/len(pearson))
    # regressor.fit(X_train, y_train)
    # predicted_X = regressor.predict(X_test)
    # can use spearmanr as well, not sure what is more appropriate
    # pearson = pearsonr(y_test, predicted_X)
    f_pearson = open("pearson.txt", "w+")
    f_pearson.write(str(pearson))
    f_pearson.close()

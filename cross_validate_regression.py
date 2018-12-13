import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from constants import TRAINING_SCORE_COLUMN
from download_data import download_data
from read_data import read_data
from mpmath import mpf, mpc, mp
mp.dps = 40

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


def regression_cv(training_ontotype, training_data, rg_file, k_fold=6, cv_rg_filename="genotypes_rg.txt"):
    print("Regression calculation {}-KF:".format(k_fold))
    training_ontotype = training_ontotype.values
    training_data_rg = training_data.values.ravel()
    print(training_data_rg)
    kf = sklearn.model_selection.KFold(n_splits=k_fold, shuffle=True,random_state=0)
    correlation_r = []
    correlation_p = []
    i = 0
    for train_idx, test_idx in kf.split(training_ontotype):
        print("Len train_data: {}, Len test_data: {}".format(len(train_idx), len(test_idx)))
        X_train, X_test, y_train, y_test = training_ontotype[train_idx], training_ontotype[test_idx], training_data_rg[train_idx], training_data_rg[test_idx]
        regressor = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=0)
        regressor.fit(X_train, y_train)
        predicted_X = regressor.predict(X_test)
        pearson = pearsonr(y_test, predicted_X)
        correlation_r.append(pearson[0])
        correlation_p.append(mpf(pearson[1]))
        print("Pearsons correlation: {}, p-Value: {}".format(pearson[0], mpf(pearson[1])))
        rg_file.write("Test {}, Pearsons correlation: {}, p-Value: {}\r\n".format(i, pearson[0], mpf(pearson[1])))
        i += 1
    print("Pearsons mean correlation: {}, p-Value: {}".format(numpy.mean(correlation_r), mpf(numpy.mean(correlation_p))))
    rg_file.write("Pearsons mean correlation: {}, p-Value: {}\r\n".format(numpy.mean(correlation_r), mpf(numpy.mean(correlation_p))))
    

ontology, associations, training_data = read_data()
print(training_data[TRAINING_SCORE_COLUMN].sample(frac=1, random_state=0))
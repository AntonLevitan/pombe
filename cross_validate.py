import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot
import numpy
import scipy
import sklearn.ensemble
import sklearn.metrics
import sklearn.model_selection
from scipy.stats import spearmanr, pearsonr
from mpmath import mpf, mpc, mp
mp.dps = 40
CV_FILE_SUFFIX = ".png"


def cross_validate(training_ontotype, training_scores):
    X = training_ontotype.values
    y = training_scores.values.ravel()

    cv = sklearn.model_selection.StratifiedKFold(n_splits=5, random_state=15)
    classifier = sklearn.ensemble.RandomForestClassifier(n_jobs=-1, random_state=15)
    probas_ = sklearn.model_selection.cross_val_predict(classifier, X, y, method="predict_proba", cv=cv, n_jobs=6)[:, 1]

    tprs = []
    aucs = []
    mean_fpr = numpy.linspace(0, 1, 100)

    i = 0
    for train, test in cv.split(X, y):
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(y[test], probas_[test])
        tprs.append(scipy.interp(mean_fpr, fpr, tpr))
        tprs[-1][0] = 0.0
        roc_auc = sklearn.metrics.auc(fpr, tpr)
        aucs.append(roc_auc)
        matplotlib.pyplot.plot(fpr, tpr, lw=1, alpha=0.3, label="ROC fold %d (AUC = %0.2f)" % (i, roc_auc))

        i += 1
    matplotlib.pyplot.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label="Luck", alpha=.8)

    mean_tpr = numpy.mean(tprs, axis=0)
    mean_tpr[-1] = 1.0
    mean_auc = sklearn.metrics.auc(mean_fpr, mean_tpr)
    std_auc = numpy.std(aucs)
    matplotlib.pyplot.plot(mean_fpr, mean_tpr, color='b', label=r"Mean ROC (AUC = %0.2f $\pm$ %0.2f)" % (mean_auc, std_auc), lw=2, alpha=.8)

    std_tpr = numpy.std(tprs, axis=0)
    tprs_upper = numpy.minimum(mean_tpr + std_tpr, 1)
    tprs_lower = numpy.maximum(mean_tpr - std_tpr, 0)
    matplotlib.pyplot.fill_between(mean_fpr, tprs_lower, tprs_upper, color="grey", alpha=.2, label=r"$\pm$ 1 std. dev.")

    matplotlib.pyplot.xlim([-0.05, 1.05])
    matplotlib.pyplot.ylim([-0.05, 1.05])
    matplotlib.pyplot.xlabel("False Positive Rate")
    matplotlib.pyplot.ylabel("True Positive Rate")
    matplotlib.pyplot.title("Receiver operating characteristic")
    matplotlib.pyplot.legend(loc="lower right")
    matplotlib.pyplot.savefig("pombe" + CV_FILE_SUFFIX)
    matplotlib.pyplot.show()


# def regression(training_ontotype, training_scores):
#     X = training_ontotype.values
#     y = training_scores.values.ravel()
#     cv = sklearn.model_selection.StratifiedKFold(n_splits=5, random_state=15)
#     regressor = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=15)
#     probas_ = sklearn.model_selection.cross_val_predict(regressor, X, y, cv=cv, n_jobs=6)
    
#     pearson = []

#     for train, test in cv.split(X, y):
#         regressor.fit(X[train], y[train])
#         cv_x = pearsonr(y[test], probas_[test])
#         pearson.append(cv_x[0])

#     pearson.append(sum(pearson)/len(pearson))
#     f_pearson = open("pearson.txt", "w+")
#     f_pearson.write(str(pearson))
#     f_pearson.close()


def regression_cv(training_ontotype, training_data, rg_file, k_fold=6, cv_rg_filename="genotypes_rg.txt"):
    print("Regression calculation {}-KF:".format(k_fold))
    training_ontotype = training_ontotype.values
    training_data_rg = training_data.values.ravel()
    kf = sklearn.model_selection.KFold(n_splits=k_fold, shuffle=True, random_state=0)
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

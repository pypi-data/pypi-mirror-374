from density_aware_smote.smote import DensityAwareSMOTE
from density_aware_smote.utils import load_dataset, train_test_split_data
from density_aware_smote.visualization import plot_class_distribution
from density_aware_smote.evaluation import evaluate_model
from sklearn.ensemble import RandomForestClassifier

def run_pipeline(dataset_path):
    data = load_dataset(dataset_path)
    X, y = data.iloc[:, :-1], data.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split_data(X, y)

    smote = DensityAwareSMOTE()
    X_res, y_res = smote.fit_resample(X_train.values, y_train.values)

    plot_class_distribution(y_train, y_res)

    clf = RandomForestClassifier(random_state=42)
    clf.fit(X_res, y_res)

    evaluate_model(clf, X_test, y_test)

if __name__ == "__main__":
    run_pipeline("data.csv")

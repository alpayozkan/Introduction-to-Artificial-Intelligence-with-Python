import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)

        evidence = []
        labels = []
        CAL = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5, 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}

        for row in reader:
            tmp_evd = []
            # administrative
            tmp_evd.append(int(row[0]))
            tmp_evd.append(float(row[1]))
            # informational
            tmp_evd.append(int(row[2]))
            tmp_evd.append(float(row[3]))
            # productrelated
            tmp_evd.append(int(row[4]))
            tmp_evd.append(float(row[5]))
            # google analytics
            tmp_evd.append(float(row[6]))
            tmp_evd.append(float(row[7]))
            tmp_evd.append(float(row[8]))
            tmp_evd.append(float(row[9]))
            # month 
            tmp_evd.append(CAL[row[10]])
            # os browser region traffic
            tmp_evd.append(int(row[11]))
            tmp_evd.append(int(row[12]))
            tmp_evd.append(int(row[13]))
            tmp_evd.append(int(row[14]))
            # visitor type
            tmp_evd.append(int(row[15] == 'Returning_Visitor'))
            # weekend
            tmp_evd.append(int(row[16] == 'TRUE'))

            # evidence
            evidence.append(tmp_evd)
            #label
            labels.append(int(row[17] == 'TRUE'))

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)

    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    total = [0, 0]
    count = [0, 0]

    for actual, predicted in zip(labels, predictions):
        total[actual] += 1
        if actual == predicted:
            count[actual] += 1
            
    sensitivity = count[1]/total[1]
    specificity = count[0]/total[0]

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()

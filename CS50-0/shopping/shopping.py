import csv
import pandas as pd
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4

month_mapping = {
    'Jan': 0,
    'Feb': 1,
    'Mar': 2,
    'Apr': 3,
    'May': 4,
    'June': 5,
    'Jul': 6,
    'Aug': 7,
    'Sep': 8,
    'Oct': 9,
    'Nov': 10,
    'Dec': 11
}
visitor_mapping = {
    'New_Visitor': 0,
    'Returning_Visitor': 1,
    'Other': 0
}
weekend_mapping = {
    'TRUE': 1,
    'FALSE': 0
}
revenue_mapping = {
    'TRUE': 1,
    'FALSE': 0
}


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    # evidence, labels = load_data("/Users/dsparks/Github/Projects/CS50-0/shopping/shopping.csv")
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


def transform_data(list):
    """
    Transform the data so that the imported data matches the required types for
    each item (integer, float, etc)
    """
    list[0] = int(list[0])                     # Administrative
    list[1] = float(list[1])                   # Administrative_Duration
    list[2] = int(list[2])                     # Informational
    list[3] = float(list[3])                   # Information_Duration
    list[4] = int(list[4])                     # ProductRelated
    list[5] = float(list[5])                   # ProductRelated_Duration
    list[6] = float(list[6])                   # BounceRates
    list[7] = float(list[7])                   # ExitRates
    list[8] = float(list[8])                   # PageValues
    list[9] = float(list[9])                   # SpecialDay
    list[10] = int(month_mapping[list[10]])    # Month
    list[11] = int(list[11])                   # OperatingSystems
    list[12] = int(list[12])                   # Browser
    list[13] = int(list[13])                   # Region
    list[14] = int(list[14])                   # TrafficType
    list[15] = int(visitor_mapping[list[15]])  # VisitorType
    list[16] = int(weekend_mapping[list[16]])  # Weekend
    list[17] = int(revenue_mapping[list[17]])  # Revenue


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the first n-1
    values in each row.
    
    labels should be the corresponding list of labels (the last value in each row),
    where each label is 1 if Revenue is true, and 0 otherwise.

    assumes the first row in the input file is a header row (so it's skipped)
    """

    # Start off with nothing ; ) 
    evidence = []
    labels = []

    # Open input file (safely) and read/parse the csv data
    try:
        with open(filename, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                transform_data(row)
                evidence.append(row[:-1])  # Extract evidence (all but the last element)
                labels.append(row[-1])     # Extract label (last element)

    # Handle file open errors if needed
    except FileNotFoundError as e:
        print(f"Could not open, file not found: {e}")
    except Exception as e:
        print(f"An unexpected error occured when trying to open file: {e}")
    
    # Return the parsed data
    return evidence, labels


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
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    # Initialize counters for true positives and true negatives
    positives = 0
    negatives = 0

    # Iterate through the labels and predictions
    for label, prediction in zip(labels, predictions):
        if label == 1 and prediction == 1:
            positives += 1
        elif label == 0 and prediction == 0:
            negatives += 1

    # Calculate sensitivity (true positive rate)
    sensitivity = positives / sum(labels)

    # Calculate specificity (true negative rate)
    specificity = negatives / (len(labels) - sum(labels))

    return sensitivity, specificity


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

import pandas as pd  
import numpy as np 
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.externals.joblib import dump, load

class RandomForest():
    def __init__(self, dataset):
        self.encoder = LabelEncoder()
        self.dataset = dataset.apply(LabelEncoder().fit_transform)

        self.x_labels = ['age', 'stars', 'languages', 'main_language', 'owner_type', 'integrators', 'has_license', 'domain', 'has_contributing', 'has_wiki', 'time_for_merge', 'has_code_of_conduct', 'has_issue_template', 'has_pull_request_template']
        self.y_label = ['cluster']

        self.x = self.dataset[self.x_labels]
        self.y = self.dataset[self.y_label]
        
        self.remove_high_correlation()

        stratified_split = StratifiedShuffleSplit(n_splits=1, test_size=0.3)
        stratified_split.get_n_splits(self.x.values, self.y.values)
        

        for train_index, test_index in stratified_split.split(self.x.values, self.y.values):
            self.x_train, self.x_test = self.x.values[train_index], self.x.values[test_index]
            self.y_train, self.y_test = self.y.values[train_index], self.y.values[test_index]

        self.standardize_features()
        self.run_classifier()

    def remove_high_correlation(self):
        threshold = 0.7
        correlation_matrix = self.x.corr(method='spearman')

        for i in range(len(correlation_matrix.columns)):
            for j in range(i):
                if correlation_matrix.iloc[i, j] >= threshold:
                    removed_feature = correlation_matrix.columns[i]

                    if removed_feature in self.x.columns:
                        print('Removing column ' + removed_feature + ' highly correlated with ' + correlation_matrix.columns[j])
                        print('Spearmans Rho: ' + str(correlation_matrix.iloc[i, j]) + ' (Greater than 0.7)')
                        self.x = self.x.drop(removed_feature, 1)

    def standardize_features(self):
        scaler = StandardScaler()
        self.x_train = scaler.fit_transform(self.x_train)
        self.x_test = scaler.transform(self.x_test)

    def run_classifier(self):
        classifier = RandomForestClassifier(n_estimators = 50, random_state = 46)
        classifier.fit(self.x_train, self.y_train.ravel())

        y_pred = classifier.predict(self.x_test)
        
        print('Saving the classifier model in "classifier.joblib" file')
        dump(classifier, 'classifier.joblib')

        print('Saving the classifier output in "classification-report.txt" file')
        with open('classification-report.txt', 'w') as report_file:
            report_file.write('# Classification Report:\n')
            report_file.write(classification_report(self.y_test, y_pred))
            print(classification_report(self.y_test, y_pred))

            report_file.write('\n# Feature Importances:\n')
            for importance in zip(self.x_labels, classifier.feature_importances_):
                report_file.write(str(importance) + '\n')
                print(importance)

            report_file.write('\n# Accuracy Score:\n')
            report_file.write(str(accuracy_score(self.y_test, y_pred)))
            print(accuracy_score(self.y_test, y_pred))

dataset = pd.read_csv('../tables/summary.csv') 
random_forest = RandomForest(dataset)
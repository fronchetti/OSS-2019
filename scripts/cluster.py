#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

import os
from pyksc import ksc
from pyksc import metrics
import numpy
from collections import OrderedDict, Counter
from csv import reader, DictReader, DictWriter
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class KSC(object):
    def __init__(self, projects, time_series, dataset_folder, csv_folder, images_folder):
        self.report_file = open('clustering-report.txt', 'w')
        self.dataset_folder = dataset_folder
        self.csv_folder = csv_folder
        self.images_folder = images_folder

        self.projects = projects
        self.time_series = numpy.array(time_series)
        self.clusters_by_time_series = {}
        self.centroids = None
        self.assign = None
        self.best_shift = None
        self.cent_dists = None

    def calculate_beta_cv(self):
        if self.assign is not None:
            return metrics.beta_cv(self.time_series, self.assign)

    def plot_beta_cv(self, min_clusters=2, max_clusters=16):
        k_clusters = [k_i for k_i in range(min_clusters, max_clusters)]
        beta_cv = []

        print('Saving βCV values in "clustering-report.txt" file')
        self.report_file.write('# βCV (for 2 ≤ k ≤ 15):\n')

        for k_i in k_clusters:
            self.get_clusters(k_i)
            beta_cv_i = self.calculate_beta_cv()
            beta_cv.append(beta_cv_i)
            self.report_file.write(str(k_i) + ': ' + str(beta_cv_i) + '\n')

        figure = plt.figure()
        plt.plot(k_clusters, beta_cv, color='black')
        plt.xlabel('# Clusters', fontsize=18)
        plt.ylabel(r'$\beta$cv', fontsize=18)
        plt.title(r'$\beta$cv for 2 $\leq$ k $\leq$ 15')
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)
        figure.savefig(self.images_folder + '/beta_cv.eps', bbox_inches='tight', format='eps', dpi=1000)

    def get_clusters(self, number_of_clusters):
        self.centroids, self.assign, self.best_shift, self.cent_dists = ksc.ksc(self.time_series, number_of_clusters)


        if self.assign is not None:
            for series, cluster in zip(self.time_series , self.assign):
                if cluster in self.clusters_by_time_series.keys():
                    self.clusters_by_time_series[cluster].append(series)
                else:
                    self.clusters_by_time_series[cluster] = [series]

    def plot_clusters(self, k):
        self.get_clusters(k)
        weeks = None 

        for cluster in self.clusters_by_time_series.keys():
            figure = plt.figure()

            for project_time_series in self.clusters_by_time_series[cluster]:
                if weeks is None:
                    weeks = [-i for i in range(len(project_time_series) - 1, -1, -1)]

                project_time_series = [0 if i == 0.1 else int(i) for i in project_time_series]

                plt.plot(weeks, project_time_series, color='black')

            plt.ylim([0, 475])
            plt.xlim([-75, 3])
            plt.xlabel('Week', fontsize=24)
            plt.ylabel('# Newcomers', fontsize=24)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)

            filename = self.images_folder + '/cluster_' + str(cluster) + '.eps'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='eps', dpi=1000)

    def plot_centroids(self):
        weeks = None

        print('Saving K-Spectral Centroids (KSC) in "clustering-report.txt" file')
        self.report_file.write('\n# K-Spectral Centroids (KSC):\n')

        for cluster, centroid in zip(range(0, 3), self.centroids):
            growth_rate = centroid[0] + centroid[-1] * 100
            self.report_file.write(str(cluster) + ': ' + str(centroid) + ' (Growth:' + str("{0:.2f}".format(growth_rate)) + ')\n')

            if weeks is None:
                weeks = [-i for i in range(len(centroid) - 1, -1, -1)]

            figure = plt.figure()
            plt.plot(weeks, centroid, color='black')
            plt.ylim([0, 0.5])
            plt.xlim([-75, 3])
            plt.xlabel('Week', fontsize=24)
            plt.ylabel('Average', fontsize=24)
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
            
            filename = self.images_folder + '/centroid_' + str(cluster) + '.eps'

            if os.path.isfile(filename):
                os.remove(filename)

            figure.savefig(filename, bbox_inches='tight', format='eps', dpi=1000)

    def insert_clusters_in_summary_file(self):
        summary_file = open(self.csv_folder + '/summary.csv', 'r')
        summary = DictReader(summary_file)
        output = []    

        if self.assign is not None:
            print('Saving # repositories per cluster in "clustering-report.txt" file')
            self.report_file.write('\n# Repositories (per Cluster):\n')
            total_of_repositories = len(self.assign)
            repositories_per_cluster = Counter(self.assign)

            for cluster in repositories_per_cluster.keys():
                number_of_repositories = repositories_per_cluster[cluster]
                percentage = float(number_of_repositories) / float(total_of_repositories) * 100
                self.report_file.write(str(cluster) + ': ' + str(number_of_repositories) + ' (%:' + str("{0:.2f}".format(percentage)) + ')\n')

        for project in summary:
             for name, time_series, cluster in zip(self.projects, self.time_series, self.assign):
                if project['name'] == str(name):
                    project['cluster'] = cluster
                    output.append(project)

        output_file = open(self.csv_folder + '/summary.csv', 'w')

        if 'cluster' in summary.fieldnames:
            writer = DictWriter(output_file, fieldnames=summary.fieldnames)
        else:
            writer = DictWriter(output_file, fieldnames=summary.fieldnames + ['cluster'])

        writer.writeheader()
        
        for project in output:
            writer.writerow(project)

if __name__ == '__main__':
    dataset_folder = '../dataset'
    csv_folder = '../tables'
    images_folder = '../plots/'

    newcomers_inflow_file = open(csv_folder + '/inflow.csv' , 'r')
    newcomers_inflow = DictReader(newcomers_inflow_file)
    projects = []
    time_series = []

    for project in newcomers_inflow:
        project_name = project['project']
        project_time_series = [project[column] for column in newcomers_inflow.fieldnames if column != 'project']
        project_time_series = [0.1 if value == '0' else int(value) for value in project_time_series]
        projects.append(project_name)
        time_series.append(project_time_series)

    k_spectral = KSC(projects, time_series, dataset_folder, csv_folder, images_folder)
    k_spectral.plot_beta_cv()
    k_spectral.plot_clusters(3)
    k_spectral.plot_centroids()
    k_spectral.insert_clusters_in_summary_file()
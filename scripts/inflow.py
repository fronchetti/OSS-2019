#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  "Felipe Fronchetti"
__contact__ = "fronchetti@usp.br"

import os
import csv
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from collections import Counter

class NewcomersInflow():
    def __init__(self, projects, csv_folder, dataset_folder):
        self.csv_folder = csv_folder
        self.dataset_folder = dataset_folder

        projects_created_at = []

        for language in projects.keys():
            repositories = projects[language]['items']

            for repository in repositories:
                created_at = datetime.strptime(repository['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                projects_created_at.append(created_at)

        self.latest_created_at = max(projects_created_at)
        weekly_series = self.get_weekly_series(projects)
        weekly_min, weekly_max = self.get_number_of_weeks(weekly_series)        
        self.export_newcomers_inflow(weekly_series, weekly_min, weekly_max)

    def get_weekly_series(self, projects):
        weekly_series = {}

        for language in projects.keys():
            repositories = projects[language]['items']

            for repository in repositories:
                project_folder = self.dataset_folder + '/' + language + '/' + repository['name']
                project_weekly_series = self.get_project_weekly_series(project_folder)
                weekly_series[repository['full_name']] = project_weekly_series

        return weekly_series

    def get_project_weekly_series(self, folder):
        commits_file = json.load(open(folder + '/commits.json', 'r'))
        newcomers_list = []
        entry_list = []

        for line in commits_file:
            newcomer = line['commit']['author']['name']
            commit_date = line['commit']['author']['date']

            if commit_date is not None:
                if newcomer is not None:
                    commit_date = datetime.strptime(commit_date, '%Y-%m-%dT%H:%M:%SZ').date()
                    
                    if commit_date >= self.latest_created_at:
                        if newcomer not in newcomers_list:
                            newcomers_list.append(newcomer)
                            entry_list.append(commit_date)

        ordered_entry_list = Counter(entry_list)

        return ordered_entry_list

    def get_number_of_weeks(self, weekly_series):
        weekly_max = None
        weekly_min = None

        for series in weekly_series.values():
            if series:
                if weekly_min is not None:
                    if min(series) < weekly_min:
                        weekly_min = min(series)
                else:
                    weekly_min = min(series)

                if weekly_max is not None:
                    if max(series) > weekly_max:
                        weekly_max = max(series)
                else:
                    weekly_max = max(series)

        return weekly_min, weekly_max

    def export_newcomers_inflow(self, weekly_series, weekly_min, weekly_max):
        fieldnames = []
        step = timedelta(days=1)

        while weekly_min <= weekly_max:
            week = (weekly_min.isocalendar()[1], weekly_min.year)
            if not week in fieldnames:
                fieldnames.append(week)
            weekly_min += step
        
        with open(self.csv_folder + '/inflow.csv', 'w') as inflow_file:
            writer = csv.DictWriter(inflow_file, fieldnames=['project'] + fieldnames)
            writer.writeheader()
        
        for project in weekly_series:
            inflow = {}
            inflow['project'] = project
            number_of_newcomers = 0

            for week in fieldnames:
                for entry_date in weekly_series[project]:
                    entry_date = (entry_date.isocalendar()[1], entry_date.year)
                    if entry_date == week:
                        number_of_newcomers = number_of_newcomers + 1
                inflow[week] = number_of_newcomers

            with open(self.csv_folder + '/inflow.csv', 'a') as inflow_file:
                writer = csv.DictWriter(inflow_file, fieldnames=['project'] + fieldnames)
                writer.writerow(inflow)

if __name__ == '__main__':
    dataset_folder = '../dataset'
    csv_folder = '../tables'

    if os.path.isfile(dataset_folder + '/projects.json'):
        with open(dataset_folder + '/projects.json', 'r') as projects_file:
            projects = json.load(projects_file)

    inflow = NewcomersInflow(projects, csv_folder, dataset_folder)
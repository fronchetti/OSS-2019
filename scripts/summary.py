#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

import os
import csv
import json
import numpy
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta

class Summary():
    def __init__(self, repository, folder):
        self.folder = folder
        self.domains = {}

        with open('../tables/domains.csv', 'r') as domains_file:
            domains = csv.DictReader(domains_file)

            for domain in domains:
                self.domains[domain['name']] = domain['domain']

    def get_time_for_merge(self):
        pull_requests_file = json.load(open(self.folder + '/pull_requests.json', 'r'))
        time_for_merge = []

        for line in pull_requests_file:
            merged_date =  line['merged_at']
            created_date = line['created_at']

            if merged_date is not None:
                merged_date = datetime.strptime(merged_date, '%Y-%m-%dT%H:%M:%SZ').date()
                created_date = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%SZ').date()
                delta = merged_date - created_date
                interval = delta.days
                time_for_merge.append(interval)

        return time_for_merge

    def get_integrators(self):
        pull_requests_file = json.load(open(self.folder + '/pull_requests.json', 'r'))
        integrators = []

        for line in pull_requests_file:
            if 'merged_by' in line:
                merged_by = line['merged_by']

                if merged_by is not None:
                    if 'login' in line['merged_by']:
                        integrator = line['merged_by']['login']
                    else:
                        integrator = 'Anonymous'
                    
                    if core_member not in integrators:
                        integrators.append(integrator)

        return integrators

    def get_newcomers(self):
        commits_file = json.load(open(self.folder + '/commits.json', 'r'))
        newcomers_list = []

        about_file = json.load(open(self.folder + '/about.json', 'r'))
        created_at = datetime.strptime(about_file['created_at'], '%Y-%m-%dT%H:%M:%SZ') + relativedelta(months=6)

        for line in commits_file:
            newcomer = line['commit']['author']['name']
            commit_date = line['commit']['author']['date']

            if commit_date is not None:
                if newcomer is not None:
                    commit_date = datetime.strptime(commit_date, '%Y-%m-%dT%H:%M:%SZ').date()

                    if commit_date >= created_at.date():
                        if newcomer not in newcomers_list:
                            newcomers_list.append(newcomer)

        return newcomers_list

    def get_contributors(self):
        commits_file = json.load(open(self.folder + '/commits.json', 'r'))
        contributors_list = []

        for line in commits_file:
            contributor = line['commit']['author']['name']

            if contributor is not None:
                if contributor not in contributors_list:
                    contributors_list.append(contributor)

        return contributors_list        

    def get_stars(self):
        stars_file = json.load(open(self.folder + '/stars.json', 'r'))
        stars_list = []

        for line in stars_file:
            star_date = line['starred_at']

            if star_date is not None:
                star_date = datetime.strptime(star_date, '%Y-%m-%dT%H:%M:%SZ').date()
                stars_list.append(star_date)

        return stars_list

    def get_forks(self):
        forks_file = json.load(open(self.folder + '/forks.json', 'r'))
        forks_list = []

        for line in forks_file:
            fork_date = line['created_at']

            if fork_date is not None:
                fork_date = datetime.strptime(fork_date, '%Y-%m-%dT%H:%M:%SZ').date()
                forks_list.append(fork_date)

        return forks_list

    def get_domain(self):
        if repository['full_name'] in self.domains.keys():
            domain = self.domains[repository['full_name']]
        else:
            domain = 'Undefined'
        return domain

    def get_used_languages(self):
        used_languages = json.load(open(self.folder + '/languages.json', 'r'))
        return used_languages

    def has_readme(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['readme'] is not None:
            return True
        else:
            return False

    def has_contributing(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['contributing'] is not None:
            return True
        else:
            return False

    def has_code_of_conduct(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['code_of_conduct'] is not None:
            return True
        else:
            return False

    def has_license(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['license'] is not None:
            return True
        else:
            return False

    def has_pull_request_template(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['pull_request_template'] is not None:
            return True
        else:
            return False

    def has_issue_template(self):
        metrics = json.load(open(self.folder + '/metrics.json', 'r'))

        if metrics['files']['issue_template'] is not None:
            return True
        else:
            return False

    def has_wiki(self):
        about_file = json.load(open(self.folder + '/about.json', 'r'))
        return about_file['has_wiki']

if __name__ == '__main__':
    dataset_folder = '../dataset'
    csv_folder = '../tables'

    if os.path.isfile(dataset_folder + '/projects.json'):
        with open(dataset_folder + '/projects.json', 'r') as projects_file:
            projects = json.load(projects_file)

    fieldnames = ['name',
                  'owner',
                  'created_at',
                  'github_url',
                  'stars',
                  'forks',
                  'has_contributing',
                  'has_readme',
                  'has_code_of_conduct',
                  'has_pull_request_template',
                  'has_issue_template',
                  'has_wiki',
                  'has_license',
                  'languages',
                  'age',
                  'domain',
                  'main_language',
                  'owner_type',
                  'newcomers',
                  'contributors',
                  'integrators',
                  'time_for_merge']

    with open(csv_folder + '/summary.csv', 'w') as summary_file:
        writer = csv.DictWriter(summary_file, fieldnames=fieldnames)
        writer.writeheader()

    for language in projects.keys():
        repositories = projects[language]['items']

        for repository in repositories:
            project_folder = dataset_folder + '/' + language + '/' + repository['name']
            project = Summary(repository, project_folder)

            created_at = datetime.strptime(repository['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
            star_total = project.get_stars()
            fork_total = project.get_forks()
            used_languages = project.get_used_languages()
            has_contributing = project.has_contributing()
            has_readme = project.has_readme()
            has_code_of_conduct = project.has_code_of_conduct()
            has_pull_request_template = project.has_pull_request_template()
            has_issue_template = project.has_issue_template()
            has_wiki = project.has_wiki()
            has_license = project.has_license()
            owner_type = repository['owner']['type']
            main_language = repository['language']
            age = 2018 - int(created_at.year)
            application_domain = project.get_domain()
            newcomers = project.get_newcomers()
            contributors = project.get_contributors()
            integrators = project.get_integrators()
            time_for_merge = project.get_time_for_merge()

            with open(csv_folder + '/summary.csv', 'a') as summary_file:
                writer = csv.DictWriter(summary_file, fieldnames=fieldnames)
                data = {'name': repository['full_name'],
                        'owner': repository['owner']['login'],
                        'created_at': created_at,
                        'github_url': repository['html_url'],
                        'stars': len(numpy.nan_to_num(star_total)),
                        'forks': len(numpy.nan_to_num(fork_total)),
                        'has_contributing': has_contributing,
                        'has_readme': has_readme,
                        'has_code_of_conduct': has_code_of_conduct,
                        'has_pull_request_template': has_pull_request_template,
                        'has_issue_template': has_issue_template,
                        'has_wiki': has_wiki,
                        'has_license': has_license,
                        'languages': len(used_languages),
                        'age': age,
                        'domain': application_domain,
                        'main_language': main_language,
                        'owner_type': owner_type,
                        'newcomers': len(numpy.nan_to_num(newcomers)),
                        'contributors': len(numpy.nan_to_num(contributors)),
                        'integrators': len(numpy.nan_to_num(integrators)),
                        'time_for_merge': int(numpy.nan_to_num(numpy.average(time_for_merge)))}

                writer.writerow(data)

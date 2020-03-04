#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

class Repository:

    def __init__(self, organization, name, collector):
        self.name = name
        self.organization = organization
        self.github = collector

    def about(self):
        print('[Repository] Returning general information about' + self.name)
        return self.github.request('repos/' + self.organization + '/' + self.name)

    def languages(self):
        print('[Repository] Returning languages used in the project')
        return self.github.request('repos/' + self.organization + '/' + self.name + '/languages')

    def commit(self, sha):
        print('[Repository] Returning commit ' + str(sha) + ' in ' + self.name)
        return self.github.request('repos/' + self.organization + '/' + self.name + '/commits/' + str(sha))

    def pull_request(self, number):
        print('[Repository] Returning pull-request #' + str(number) + ' in ' + self.name)
        return self.github.request('repos/' + self.organization + '/' + self.name + '/pulls/' + str(number))

    def issue(self, number):
        print('[Repository] Returning issue #' + str(number) + ' in ' + self.name)
        return self.github.request('repos/' + self.organization + '/' + self.name + '/issues/' + str(number))
    
    def community_metrics(self):
        print('[Repository] Returning community metrics of project ' + self.name)
        return self.github.request('repos/' + self.organization + '/' + self.name + '/community/profile', headers={'Accept': 'application/vnd.github.black-panther-preview+json'})

    def readme(self):
        print('[Repository] Returning README.md file of project ' + self.name)
        metrics = self.community_metrics()
        readme = []

        if metrics['files']['readme']:
            if 'url' in metrics['files']['readme']:
                description_url = metrics['files']['readme']['url']
                description = self.github.custom_request(description_url, file_type='json')
                readme = self.github.custom_request(description['download_url'])
        return readme

    def contributing(self):
        print('[Repository] Returning CONTRIBUTING.md file of project ' + self.name)
        metrics = self.community_metrics()
        contributing = []

        if metrics['files']['contributing']:
            if 'url' in metrics['files']['contributing']:
                description_url = metrics['files']['readme']['url']
                description = self.github.custom_request(description_url, file_type='json')
                contributing = self.github.custom_request(description['download_url'])
        return contributing

    def commits(self, sha=None, path=None, author=None, since=None, until=None, page_range={}):
        print('[Repository] Returning commits available in ' + self.name)

        commits = []
        parameters = {}

        if sha is not None:
            parameters['sha'] = sha
        if path is not None:
            parameters['path'] = path
        if author is not None:
            parameters['author'] = author
        if since is not None:
            paramethers['since'] = since
        if until is not None:
            paramethers['until'] = until

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = str(page_number)
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/commits', parameters)

                if request:
                    for commit in request:
                        commits.append(commit)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/commits', parameters)

                if request:
                    for commit in request:
                        commits.append(commit)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return commits
    
    def pull_requests(self, state=None, direction=None, sort=None, base=None, head=None, page_range={}):
        print('[Repository] Returning pull-requests available in ' + self.name)
        pull_requests = []
        parameters = {}

        if state is not None:
            parameters['state'] = state
        if direction is not None:
            parameters['direction'] = direction
        if sort is not None:
            parameters['sort'] = sort
        if base is not None:
            parameters['base'] = base
        if head is not None:
            parameters['head'] = head

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/pulls', parameters)

                if request:
                    for pull_request in request:
                        pull_requests.append(pull_request)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/pulls', parameters)

                if request:
                    for pull_request in request:
                        if pull_request:
                            if 'number' in pull_request:
                                pull_request = self.pull_request(pull_request['number'])
                                pull_request['reviews'] = self.pull_request_reviews(pull_request['number'])
                                pull_request['comments'] = self.pull_request_comments(pull_request['number'])
                                pull_requests.append(pull_request)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return pull_requests

    def pull_request_reviews(self, number, page_range={}):
        reviews = []
        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/pulls' + '/' + str(number) + '/comments', {'page': str(page_number)})

                if request:
                    for review in request:
                        reviews.append(review)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/pulls' + '/' + str(number) + '/comments', {'page': str(page_number)})

                if request:
                    for review in request:
                        reviews.append(review)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return reviews

    def pull_request_comments(self, number, page_range={}):
        comments = []
        
        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/issues' + '/' + str(number) + '/comments', {'page': str(page_number)})

                if request:
                    for comment in request:
                        comments.append(comment)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/issues' + '/' + str(number) + '/comments', {'page': str(page_number)})

                if request:
                    for comment in request:
                        comments.append(comment)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return comments


    def issues(self, state=None, direction=None, milestone=None, labels=None, creator=None, since=None, assignee=None, mentioned=None, page_range={}):
        print('[Repository] Returning issues available in ' + self.name)

        issues = []
        parameters = {}

        if state is not None:
            parameters['state'] = state
        if direction is not None:
            parameters['direction'] = direction
        if labels is not None:
            parameters['labels'] = labels
        if creator is not None:
            parameters['creator'] = creator
        if since is not None:
            parameters['since'] = since
        if milestone is not None:
            parameters['milestone'] = milestone
        if mentioned is not None:
            parameters['mentioned'] = mentioned
        if assignee is not None:
            parameters['assignee'] = assignee

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/issues', parameters)

                if request:
                    for issue in request:
                        issues.append(issue)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/issues', parameters)

                if request:
                    for issue in request:
                        issues.append(issue)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return issues

    def contributors(self, anonymous='false', page_range={}):
        print('[Repository] Returning contributors of ' + self.name)

        contributors = []
        parameters = {}

        if anonymous:
            parameters['anonymous'] = anonymous

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/contributors', parameters)

                if request:
                    for contributor in request:
                        contributors.append(contributor)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/contributors', parameters)

                if request:
                    for contributor in request:
                        contributors.append(contributor)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return contributors


    def stars(self, page_range={}):
        print('[Repository] Returning stars available in ' + self.name)

        stars = []

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/stargazers', {'page': str(page_number)}, {'Accept': 'application/vnd.github.v3.star+json'})

                if request:
                    for star in request:
                        stars.append(star)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/stargazers', {'page': str(page_number)}, {'Accept': 'application/vnd.github.v3.star+json'})

                if request:
                    for star in request:
                        stars.append(star)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return stars

    def forks(self, sort=None, page_range={}):
        print('[Repository] Returning forks available in ' + self.name)

        forks = []
        parameters = {}

        if sort is not None:
            parameters['sort'] = sort

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/forks', parameters)

                if request:
                    for fork in request:
                        forks.append(fork)
        else:
            pages_exist = True
            page_number = 1

            while(pages_exist):
                parameters['page'] = page_number
                request = self.github.request('repos/' + self.organization + '/' + self.name + '/forks', parameters)

                if request:
                    for fork in request:
                        forks.append(fork)
                else:
                    pages_exist = False

                page_number = page_number + 1

        return forks

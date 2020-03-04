#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ =  'Felipe Fronchetti'
__contact__ = 'fronchetti@usp.br'

class Search:

    def __init__(self, collector):
        self.github = collector

    def repositories(self, keywords=None, sort=None, order=None, page_range={}):
        repositories = []
        parameters = {}

        if keywords is not None:
            parameters['q'] = keywords
        else:
            raise ValueError('Keywords have not been defined')
        if sort is not None:
            parameters['sort'] = sort
        if order is not None:
            parameters['order'] = order

        if page_range:
            first_page = page_range['first_page']
            last_page = page_range['last_page']

            for page_number in range(first_page, last_page):
                parameters['page'] = page_number
                request = self.github.request('search/repositories', parameters)
                repositories.append(request)

            return repositories
        else:
            repositories = self.github.request( 'search/repositories', parameters)
            return repositories

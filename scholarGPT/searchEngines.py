from habanero import Crossref
import re

class Search_engine:
    def invoke(self, key):
        pass


def cleanhtml(raw_html):
    CLEANR = re.compile('<.*?>') 
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

class Search_engine_crossref(Search_engine):
    num_search_each_key = 100
    cr = Crossref()

    def __init__(self, num_search_each_key = 100):
        self.num_search_each_key = num_search_each_key

    def invoke(self, key):
        x = self.cr.works(query = key, limit=self.num_search_each_key)
        titles = [it.get('title', [''])[0] for it in x['message']['items']]
        abstracts = [it.get('abstract', '') for it in x['message']['items']]

        ## index of empty titles
        empty_title_index = [i for i, value in enumerate(titles) if value==""]
        ## index of empty abstracts
        # empty_abstract_index = [i for i, value in enumerate(abstracts) if value==""]
        empty_abstract_index = []
        ## index of empty titles and abstracts
        empty_title_abstract_index = empty_title_index + empty_abstract_index
        empty_title_abstract_index = list(set(empty_title_abstract_index))
        ## remove empty titles and abstracts
        titles = [value for i, value in enumerate(titles) if i not in empty_title_abstract_index]
        abstracts = [value for i, value in enumerate(abstracts) if i not in empty_title_abstract_index]

        return [{'title':t, 'abstract':cleanhtml(a)} for t,a in zip(titles, abstracts)]

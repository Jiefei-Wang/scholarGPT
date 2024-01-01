class Search_chain:
    search_engine = None
    total_num_search = 100

    def __init__(self, search_engine, total_num_search = 100):
        self.search_engine = search_engine
        self.total_num_search = total_num_search
    
    def invoke(self, keys):
        search_results = []
        for key in keys:
            x = self.search_engine.invoke(key)
            search_results.extend(x)
        
        all_titles = [it['title'] for it in search_results]

        ## index of duplicated titles
        duplicated_title_index = [i for i, value in enumerate(all_titles) if value in all_titles[:i]]

        ## remove duplicated titles
        search_results = [value for i, value in enumerate(search_results) if i not in duplicated_title_index]

        return search_results[:self.total_num_search]



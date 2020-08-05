# search.py: Elasticsearch module that is only source of Elasticsearch implementation,
# abstraction in mind so I have flexibility to switch to different search engine
# or change what text fields I want to add to search index other than just Posts.
from flask import current_app

def search_status():
    if not current_app.elasticsearch:
        print('Elasticsearch server not configured.')
    else:
        print('Elasticsearch server detected.')

def add_to_index(index, model):
    if not current_app.elasticsearch:  # allows for app to continue running even
                                       # if elasticsearch service not up
        print('none add')
        return
    payload = {}  # dictionary will specify what text fields are to be indexed per model
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(index=index, id=model.id, body=payload)

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        print('none remove')
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        print('none query')
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    # above extracts id values from much larger list of results provided by Elasticsearch
    return ids, search['hits']['total']['value']
    # returns list of id elements for search results AND total number of results

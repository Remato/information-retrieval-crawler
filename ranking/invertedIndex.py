import os
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import sys
import re
from scipy.sparse import find

count_vect = CountVectorizer(analyzer="word",
                             tokenizer=None,
                             preprocessor=None,
                             stop_words=None)


def process_text(text):
    text = re.sub(r'\W+', ' ', text)
    text = text.lower()
    return text


def get_items():
    filename = '../data/wrapped.json'
    with open(filename, encoding='utf-8') as json_file:
        json_array = json.load(json_file)
        return json_array


def process_text_in_pages(pages):
    docs = []
    for page in pages:
        docs.append(process_text(page))
    return docs


def get_inverted_index(docs, type):
    words = count_vect.fit_transform(docs)
    features = count_vect.get_feature_names()

    row, column, values = find(words)

    terms = list(zip(row, column, values))

    idf = {}
    inverse_index = {}

    for feature in features:
        idf[feature] = 0

    for (_, column, value) in terms:
        idf[features[column]] = idf[features[column]] + value

    last_row = None
    last_feature = None
    value = None

    for (row, column, value) in terms:

        actual_feature = features[column]

        if 'compress' in type:
            value = get_bytes(row)

        if 'normal' in type:
            value = [(row, value)]

        if actual_feature in inverse_index:
            inverse_index[actual_feature] = inverse_index[actual_feature] + value

        else:
            inverse_index[actual_feature] = value

        last_row = row

        last_feature = actual_feature

    return inverse_index


def get_bytes(value):
    if value < (1 << 7):
        return bytearray([value + (1 << 7)])
    x = 7
    while (value >> (x + 7)) > 0:
        x = x + 7
    return bytearray([value >> x]) + get_bytes(value - ((value >> x) << x))


# https://goshippo.com/blog/measure-real-size-any-python-object/
def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

# if __name__ == '__main__':
#     docs = []
#     for item in get_items():
#         docs.append(item['pagina'])
#     print(docs)
#     docs = process_text_in_pages(docs)
#     inverted_index = get_inverted_index(docs, 'normal')
#     inverted_index_compressed = get_inverted_index(docs, 'compress')
#     size_normal = get_size(inverted_index)
#     size_compressed = get_size(inverted_index_compressed)
#     print(inverted_index - inverted_index_compressed)
import invertedIndex
import documents

import math
from threading import Thread
n_docs = len(documents.docs)

# calculo de similaridade usando coseno | qual o documento que mais se adapta à query?
# Doc_1 = (0.5, 0.8, 0.3), Doc_2 = (0.9, 0.4, 0.2) Query = (1.5, 1.0, 0)
# similaridade = ((0.5*1.5)+(0.8*1.0)+(0.3*0))/raiz((0.5²+0.8²+0.3²)*(1.5², 1.0², 0²))
# similitaridade = s/raiz(d*q)
# o menor angulo está mais proximo

# tf-idf 
# tf  = frequencia de um termo no documento
# idf = log(1 + N/n_i) (frequency smooth)
# n_i = numero de documentos q o termo aparece
# N = numero de documentos
# então o tf-idf é so multiplicar os 2 valores


# a ideia é usar para saber qual o termo mais "especial" da pesquisa
def idf_query(query):
  terms = query.split()
  idfs = []

  for term in terms:
    if term in invertedIndex.indexes:
      occurrencies = len(invertedIndex.indexes[term])    
      idfs.append((1 + math.log(n_docs/occurrencies)))
    else:
      idfs.append(0.0)

  return idfs

def tf_idf(term, doc):
  tf = doc['body'].count(term)

  if term in invertedIndex.indexes:
    occurrencies = invertedIndex.indexes[term]
  else:
    return 0.0

  idf = math.log(1 + n_docs/len(occurrencies))

  return tf*idf
  
def rank(query):
  terms = query.split()
  docs = []

  for term in terms:
    if term in invertedIndex.indexes:
      for d in invertedIndex.indexes[term]:
        docs.append(d)

    docs = list(set(docs))
  # method document-at-a-time
  scores = []
  for doc in docs:
    score = []
    for term in terms:
      if doc in documents.docs:
        score.append(tf_idf(term, documents.docs[doc]))
    # aqui temos os tf-idf para cada doc
    scores.append(score)
    
    # usar a similaridade de cosenos para finalizar rankeamento
  rank = cos_similar(query, scores, docs)

  return rank

def cos_similar(query, scores, docs):
  query_scores = idf_query(query)
  doc_scores = []
  
  for i in range(len(docs)):
    s = 0
    d = 0
    q = 0
    for j in range(len(scores[0])):
        s = s + scores[i][j]*query_scores[j]
        d = d + math.pow(scores[i][j], 2)
        q = q + math.pow(query_scores[j], 2)

    doc_scores.append({
      'doc': docs[i],
      'score': s/math.sqrt(d*q)
    })

  doc_scores = sorted(doc_scores, key=lambda k: k['score'])

  return doc_scores

    

print('Digite a sua consulta:')
query = input()


print(rank(query))

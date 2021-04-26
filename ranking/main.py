import math
import json
import invertedIndex

# colocar o novo valor de docs
inverted = invertedIndex.process()
n_docs = 20

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
    if term in inverted:
      occurrencies = len(inverted[term])    
      idfs.append((1 + math.log(n_docs/occurrencies)))
    else:
      idfs.append(0.0)

  return idfs

def tf_idf(term, doc):
  tf = 0.0

  if term in inverted:
    occurrencies = len(inverted[term])
  
    for i in range(occurrencies):
      if inverted[term][i][0] == doc:
        tf = inverted[term][i][1]
  else:
    return 0.0

  idf = math.log(1 + n_docs/occurrencies)

  return tf*idf
  
def rank(query):
  terms = query.split()
  docs = []

  for term in terms:
    if term in inverted:
      for d in inverted[term]:
        docs.append(d[0])
  
  # rank only tf
  newbie_rank = {}
  for d in docs:
    newbie_rank[d] = float(docs.count(d))

  # parse
  parsed_newbie = []
  for r in newbie_rank:
    parsed_newbie.append({
      'doc': r,
      'score': newbie_rank[r]
    })

  parsed_newbie = sorted(parsed_newbie, key=lambda k: k['score'], reverse=True)

  # rank with tf-idf
  docs = list(set(docs))

  # method document-at-a-time
  scores = []
  for doc in docs:
    score = []
    for term in terms:
      score.append(tf_idf(term, doc))
    # aqui temos os tf-idf para cada doc
    scores.append(score)
    
    # usar a similaridade de cosenos para finalizar rankeamento
  rank = cos_similar(query, scores, docs)

  return parsed_newbie, rank

def cos_similar(query, scores, docs):
  query_scores = idf_query(query)

  doc_scores = []
  
  for i in range(len(docs)):
    s = 0.0
    d = 0.0
    q = 0.0
    for j in range(len(scores[0])):
        s = s + scores[i][j]*query_scores[j]
        d = d + math.pow(scores[i][j], 2)
        q = q + math.pow(query_scores[j], 2)

    if d > 0 and q > 0:
      doc_scores.append({
        'doc': docs[i],
        'score': s/math.sqrt(d*q)
      })
    else:
      doc_scores.append({
        'doc': docs[i],
        'score': 0.0
      })

  doc_scores = sorted(doc_scores, key=lambda k: k['score'], reverse=True)

  return doc_scores

def spearman(r1, r2):
  s = 0
  k = len(r1)

  # 100% porém não tem nenhuma pesquisa
  if k == 0:
    return 1.0

  for i in range(len(r1)):
    sub = r1[i]['score'] - r2[i]['score']
    s = s + math.pow(sub, 2)
  
  spearman = 1 - ((6*s)/(k*(math.pow(k,2) - 1)))
  
  return spearman


while(1):
  

  print('Digite uma nova consulta:')
  query = input()

  if query != '':
    newbie_rank, optimized_rank = rank(query)

    with open("../data/wrapped.json", "r") as outfile:
      documents = json.loads(outfile.read())

    print(documents[0]['link'])

    print('[ Rankeamento sem tf-idf ]')
    for n in newbie_rank:
      print(documents[n['doc']-1]["link"])
    
    print('----------------------------')

    print('[ Rankeamento com tf-idf ]')
    for o in optimized_rank:
      print(documents[o['doc']-1]["link"])

    print('----------------------------')

    # correlation spearman
    correlation = spearman(newbie_rank, optimized_rank)
    print('O fator de correlação entre essas 2 pesquisa foi de: '+ str(correlation))







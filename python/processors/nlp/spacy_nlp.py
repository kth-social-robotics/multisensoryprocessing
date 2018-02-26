import spacy
from spacy import displacy
from pathlib import Path

# Get models
nlp = spacy.load('en')
#nlp = spacy.load('en_core_web_lg')

# Get document
doc = nlp(u'Apple is looking at buying U.K. startup for $1 billion')

# Tokeniser
# for token in doc:
#     print(token.text)

# POS tagger
# for token in doc:
#     print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
#           token.shape_, token.is_alpha, token.is_stop)

# NER
# for ent in doc.ents:
#     print(ent.text, ent.start_char, ent.end_char, ent.label_)

# Word similarity
# tokens = nlp(u'dog cat banana')
# for token1 in tokens:
#     for token2 in tokens:
#         print(token1, token2, token1.similarity(token2))

# # Document similarity
doc1 = nlp(u"Paris is the largest city in France.")
doc2 = nlp(u"Vilnius is the capital of Lithuania.")
doc3 = nlp(u"An emu is a large bird.")

for doc in [doc1, doc2, doc3]:
    for other_doc in [doc1, doc2, doc3]:
        print(doc, other_doc, doc.similarity(other_doc))

# Word vectors
# tokens = nlp(u'dog cat banana sasquatch')
# for token in tokens:
#     print(token.text, token.has_vector, token.vector_norm, token.is_oov)

# Noun chunks
#print list(doc.noun_chunks)[0].text # Gets the first noun

# Visualise to svg
# doc1 = nlp(u'This is a sentence.')
# doc2 = nlp(u'This is another sentence.')
# #svg = displacy.render([doc1, doc2], style='dep', page=True)
# svg = displacy.render(doc, style='ent')
# output_path = Path('images/sentence.svg')
# output_path.open('w', encoding='utf-8').write(svg)

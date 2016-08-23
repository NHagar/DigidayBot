import nltk
import feedparser
from nltk import word_tokenize
from nltk import ConditionalFreqDist
from nltk import bigrams
import string

llog = feedparser.parse("http://www.digiday.com/feed")

l = []

for post in llog.entries:
    content = post.summary
    fp = word_tokenize(content)
    for item in fp:
        item.encode(encoding='ascii', errors='ignore')
        l.append(item)

def generate_model(cfdist, word, num=18):
    for i in range(num):
        print word,
        word = cfdist[word].max()
text = ' '.join(e for e in l if e.isalnum())
text = text.replace(" p ", " ")
text = text.replace("strong", "")
text = text.replace("img", "")
text = text.replace("http", "")
text = text.replace("alignleft", "")
text = text.replace("nofollow", "")
text = word_tokenize(text)

bgs = bigrams(text)

cfd = ConditionalFreqDist(bgs)
print list(bgs)
print cfd['Facebook']
generate_model(cfd, 'Facebook')

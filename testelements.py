import feedparser
import nltk.data
from nltk.tokenize import sent_tokenize
d = feedparser.parse("http://www.digiday.com/feed")

l = []
m = []
for post in d.entries:
    fp = post.summary
    fp = fp.replace("<p>", "")
    fp = fp.replace(("</p>"), "")
    fp = sent_tokenize(fp)
    for item in fp[0:5]:
        if len(item) <= 116:
            l.append(item)
    if len(l) >= 1:
        m.append(l[0])
        l = []
    else:
        m.append(post.title)
        l = []
print m
#    m = m + "".join(fp)
#print m
#l.append(sent_tokenize(m))

#print l
#for item in l:
#    if len(item) <= 116:
#        hed = item

#for item in l:
#    q = item[:116]
#    print q
#    if q.endswith(".") == True:
#        print q
#for item in l:
#    for sent in item:
#        if len(sent) <= 116:
#            print sent

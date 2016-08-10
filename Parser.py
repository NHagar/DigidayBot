import sqlite3
import time
import re
import feedparser
import tweepy
from random import randint
from nltk.tokenize import sent_tokenize

auth = tweepy.OAuthHandler(*)
auth.set_access_token(*)

api = tweepy.API(auth)

DATABASE = "tweets.sqlite"

conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
c = conn.cursor()

l = []

def record_links(url):

    #create the table if it doesn't exist
    c.execute('CREATE TABLE IF NOT EXISTS RSSContent (`url`, `title`, `dateAdded`, `content`, `tweeted`)')

    d = feedparser.parse(url)

    #establish loop
    while True:
        for entry in d.entries:
            #Grab first sentence
            l = []
            fp = entry.summary
            fp = fp.replace("<p>", "")
            fp = fp.replace(("</p>"), "")
            fp = sent_tokenize(fp)
            for item in fp[0:5]:
                if len(item) <= 116:
                    l.append(item)
            if len(l) >= 1:
                content = l[0]
                l = []
            else:
                content = entry.title
                l = []
		#check for duplicates
            c.execute('SELECT * FROM RSSContent WHERE url=?', (entry.link,))
            if not c.fetchall():
                t = (entry.link, entry.title, time.strftime("%Y-%m-%d", entry.updated_parsed), content)
                c.execute('INSERT INTO RSSContent (`url`, `title`,`dateAdded`, `content`) VALUES (?,?,?,?)', t)
                print l
                conn.commit()

        #Flush stories not published today
        c.execute("DELETE FROM RSSContent WHERE dateAdded!=date('now', 'localtime')")
        conn.commit()

        #get rid of sponsored content/awards posts
        c.execute("DELETE FROM RSSContent WHERE url NOT LIKE '%/brands/%' AND url NOT LIKE '%/agencies/%' AND url NOT LIKE '%/publishers/%' AND url NOT LIKE '%/platforms/%' AND url NOT LIKE '%/uk/%'")
        conn.commit()

        #Insert story text

        #Restart if everything has been tweeted
        c.execute('SELECT COUNT(`tweeted`) FROM RSSContent')
        for row in c:
            checker = row[0]
            print checker
        c.execute('SELECT COUNT(`title`) FROM RSSContent')
        for row in c:
            altchecker = row[0]
            print altchecker
        if checker == altchecker:
            c.execute('UPDATE RSSContent SET `tweeted`=NULL')
            print "Restarted"
            conn.commit()

        #grab tweet copy and link
        c.execute('SELECT url, title FROM RSSContent WHERE `tweeted` IS NULL')
        tweet = c.fetchone()
        tweet_text = "%s" % (tweet[1])
        number = randint(0,100)
        number = str(number)
        tweet_link = tweet[0]+"?utm_medium=social&utm_campaign=digidaydis&utm_source=twitter&utm_content=robo"+number+"&utm_term=organic_digidayfeed"
        full_tweet = tweet_text + " " + tweet_link
        print full_tweet

        #Avoid bumping from error message
        try:
            #send, and tag tweet as tweeted
            tweeted="yes"
            c.execute('UPDATE RSSContent SET `tweeted`=? WHERE `title`=?', (tweeted, tweet_text))
            conn.commit()
            time.sleep(2)
#            api.update_status(full_tweet)

            #set to run again in 45-60 min
#            minutes = randint(45, 60)
#            print "The next tweet will go out in %s minutes" % (minutes)
#            time.sleep(60*minutes)
        except:
            pass
#            print "You've been tweeting a lot"
#            time.sleep(30)

record_links('http://digiday.com/feed')

#Alt text

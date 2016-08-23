import sqlite3
import time
import re
import feedparser
import tweepy
from random import randint
from bs4 import BeautifulSoup
from nltk import sent_tokenize
from datetime import datetime

auth = tweepy.OAuthHandler('x', 'x')
auth.set_access_token('x-x', 'x')

api = tweepy.API(auth)

DATABASE = "tweets.sqlite"

conn = sqlite3.connect(DATABASE)
conn.row_factory = sqlite3.Row
c = conn.cursor()


def record_links(url):

    #create the table if it doesn't exist
    c.execute('CREATE TABLE IF NOT EXISTS RSSContent (`url`, `title`, `dateAdded`, `content`, `tweeted`)')

    d = feedparser.parse(url)

    #establish loop
    while True:
        for entry in d.entries:
		#check for duplicates
            c.execute('SELECT * FROM RSSContent WHERE url=?', (entry.link,))
            if not c.fetchall():
                content = entry.summary
                text = BeautifulSoup(content, 'lxml').get_text()
                fp = sent_tokenize(text)
                graf = entry.content[0].value
                txt = BeautifulSoup(graf, 'lxml').get_text()
                pf = sent_tokenize(txt)
                l = fp[0:2] + pf
                for i in l:
                    if len(i) <= 116:
                        twt = i
                        break
                t = (entry.link, twt, time.strftime("%Y-%m-%d", entry.updated_parsed), content)
                c.execute('INSERT INTO RSSContent (`url`, `title`,`dateAdded`, `content`) VALUES (?,?,?,?)', t)
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
            api.update_status(full_tweet)

            #set to run again in 45-60 min
            minutes = randint(45, 60)
            print "This tweet went out at %s" % (datetime.now().time())
            print "The next tweet will go out in %s minutes" % (minutes)
            time.sleep(60*minutes)
        except:
            print "You've been tweeting a lot"
            time.sleep(30)

record_links('http://digiday.com/feed')

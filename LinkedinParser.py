import sqlite3
import time
import re
import feedparser
from linkedin import linkedin
from random import randint
from nltk.tokenize import sent_tokenize
from bs4 import BeautifulSoup
from datetime import datetime

print linkedin.__file__

API_KEY = 'x'
API_SECRET = 'x'
RETURN_URL = 'http://localhost:8000'

authentication = linkedin.LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL, linkedin.PERMISSIONS.enums.values())

application = linkedin.LinkedInApplication(token='x')

DATABASE = "linkedin.sqlite"

conn = sqlite3.connect(DATABASE)
#conn.text_factory = str
conn.row_factory = sqlite3.Row
c = conn.cursor()


def record_links(url):

    #create the table if it doesn't exist
    c.execute('CREATE TABLE IF NOT EXISTS RSSContent (`url`, `title`, `dateAdded`, `posted`)')

    d = feedparser.parse(url)

    #establish loop
    while True:
        for entry in d.entries:
		#check for duplicates
            c.execute('SELECT * FROM RSSContent WHERE url=?', (entry.link,))
            if not c.fetchall():
                fp = entry.summary
                text = BeautifulSoup(fp, 'lxml').get_text()
                body = sent_tokenize(text)
                body = body[0:1]
                body = ' '.join(body)
                t = (entry.link, body, time.strftime("%Y-%m-%d", entry.updated_parsed))
                c.execute('INSERT INTO RSSContent (`url`, `title`,`dateAdded`) VALUES (?,?,?)', t)
                conn.commit()
                body = []

        #Flush stories not published today
        c.execute("DELETE FROM RSSContent WHERE dateAdded!=date('now', 'localtime')")
        conn.commit()

        #get rid of sponsored content/awards posts
        c.execute("DELETE FROM RSSContent WHERE url NOT LIKE '%/brands/%' AND url NOT LIKE '%/agencies/%' AND url NOT LIKE '%/publishers/%' AND url NOT LIKE '%/platforms/%' AND url NOT LIKE '%/uk/%'")
        conn.commit()

        #Restart if everything has been tweeted
        c.execute('SELECT COUNT(`posted`) FROM RSSContent')
        for row in c:
            checker = row[0]
            print checker
        c.execute('SELECT COUNT(`title`) FROM RSSContent')
        for row in c:
            altchecker = row[0]
            print altchecker
        if checker == altchecker:
            c.execute('UPDATE RSSContent SET `posted`=NULL')
            print "Restarted"
            conn.commit()

        #grab post copy and link
        c.execute('SELECT url, title FROM RSSContent WHERE `posted` IS NULL')
        post = c.fetchone()
        post_text = "%s" % (post[1])
        number = randint(0,100)
        number = str(number)
        post_link = post[0]+"?utm_medium=social&utm_campaign=digidaydis&utm_source=linkedin&utm_content=robo"+number+"&utm_term=organic_digidayfeed"
        full_post = post_text + " " + post_link
        print full_post

        #Avoid bumping from error message
        try:
            #send, and tag tweet as tweeted
            posted="yes"
            c.execute('UPDATE RSSContent SET `posted`=? WHERE `title`=?', (posted, post_text))
            conn.commit()

            application.submit_company_share(company_id=418547, comment=full_post)

            #set to run again in 3 hours
            hours = 60*60*3
            print "This post went out at %s" % (datetime.now().time())
            print "The next post will go out in 3 hours"
            time.sleep(hours)
        except:
            pass
            print "That didn't work"
            time.sleep(30)

record_links('http://digiday.com/feed')

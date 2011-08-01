#!/usr/bin/env python
import urllib, string, sys, os, smtplib, time, sqlite3
from xml.dom import minidom

import rss_monitor_settings as settings

# set up database connection
db = sqlite3.connect(settings.sqlfile)
c = db.cursor()
myQuery = "create table if not exists alerts(subject text,link text,source text,date_sent text);"
c.execute(myQuery)
c = db.cursor()

# see if our filter matches a pattern, and if the record doesn't
# already exist in the DB
def filter(phrase, link):
    for pattern in settings.patterns:
        alert = True
	# print phrase
        postWords = string.split(string.lower(phrase))
        for word in pattern:
            if word not in postWords:
                alert = False
        if alert:
	    # print "checking... %s" % link
            myQuery = "select * from alerts where link=?;"
            c.execute(myQuery, (link, ))
	    r = c.fetchone()
	    # print r
            if (r == None):
                if ("--console" in sys.argv) or ("-c" in sys.argv):
                    print "New Link Found:",link
                return True
    return False

# container for the items to monitor
posts = []

# container for items to alert on
alerts = []

for f in settings.feeds:
    fp = open("tempfile","w")
    fp.write(urllib.urlopen(f).read())
    fp.close()
    try:
        xmldoc = minidom.parse("tempfile")
    except:
        print "feedMonitor - unable to read feed:", f
        sys.exit()

    items = xmldoc.getElementsByTagName("item")
    for i in items:
        myTitle = i.getElementsByTagName("title")
        myLink = i.getElementsByTagName("link")
        # each post is a tuple containing the source, link, title, description
        try:
            posts.append((f, myLink[0].firstChild.toxml(),
                          myTitle[0].firstChild.toxml()))
        except: pass

# send each post to the keyword filter
#
# any posts that match on one or more filters will be added to the
# list of alerts to be mailed
for post in posts:
    if filter(post[2], post[1]):
        alerts.append(post)

# if there are any alerts found, mail them out
if len(alerts):
    s = smtplib.SMTP(settings.smtpserver)
    msg = 'To: '
    for recipient in settings.tolist[:-1]:
        msg += recipient+', '
    msg += settings.tolist[-1]
    if len(alerts) == 1:
        msg += '\nSubject: rss Alert\n\n'
    else:
        msg += '\nSubject: rss Alerts\n\n'
    for alert in alerts:
        # strip 'CDATA' etc. from post title when building line
        msg += alert[2][9:][:-3] + " - " + alert[1] + "\n\n"
        # log the alert in the database (if not in console mode)
        if "--console" not in sys.argv:
            tstr = time.strftime('%Y-%m-%d %H:%M:%S')
            myQuery = "insert into alerts(subject,link,source,date_sent) values(?, ?, ?, ?)"
            c.execute(myQuery, (alert[2], alert[1], alert[0], tstr))
            # also: c.executemany(query, tuplarray)
            db.commit()
        
    # if console is chosen, print only to the console
    if "--console" in sys.argv:
        print "\n",msg
    else:
        # send out the mail
        s.sendmail(settings.fromaddr, settings.tolist, msg)
    
# a little housecleaning            
try:
    os.remove("tempfile")
except:
    pass


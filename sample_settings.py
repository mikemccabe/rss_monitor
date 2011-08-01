feeds = [
         'http://sfbay.craigslist.org/search/car?query=previa&srchType=T&format=rss',
	 ]

# strings to look for in the feeds
# for a pattern to match, all words in each list must be present
# in the search string
patterns = [
	['previa'], 
	]
			
# smtp server
smtpserver = 'smtp.somewhere.com'
			
# mailing list for the alerts
tolist = ['someone@somewhere.com', ]

# email address that you want the alerts to come from
fromaddr = 'someone@somewhere.com'

# database variables
sqlfile = '/home/someone/.rss_monitor_db'

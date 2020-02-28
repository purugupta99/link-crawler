#title: Program in python to crawl web pages

#importing libraries
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
# import csv
import sys, re

if len(sys.argv) < 3:
	print("Usage: python3 crawler_level.py <url> <depth>")
	quit()

seed_url = sys.argv[1]
max_depth = int(sys.argv[2])

# Initialization of Variables
# seed_url = "http://www.google.com"
# max_depth = 2

maximum_tries = 2
links_crawled = []
links_tocrawl = [[seed_url,1]]
links_broken = []
links_unvalid = ["javascript", "png", "jpeg", "jpg", "gif", "deb", "exe", "facebook", "linkedin", "ieee", "twitter.com"]
not_valid_url = 0

crawled_unvalid_links = []

#Session Creation for Request Handling
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=maximum_tries))

# Get the href links from the page source code
def getLink(page):
	href_index = page.find( '<a href=' )
	
	if href_index != -1:
		start_quote = page.find('"', href_index + 1)
		end_quote = page.find('"', start_quote + 1)
		url = page[start_quote + 1:end_quote]
		return url, end_quote
	else:
		return -1, -1

# Gets link from the list links_tocrawl to get their source code
for item in links_tocrawl:

	url = item[0] 
	depth = item[1]
	# print ("Crawling URL: " + url + ", depth :" + str(depth))
	
	# If link is broken then try for maximum number of times, and throw an exception. And move to next url is links_tocrawl list
	try:
		req = requests.get(url)
	except requests.exceptions.ConnectionError as e:
		links_broken.append(url)
		print ("Maximum retries exceeded for", url)
		links_tocrawl.pop(0)
		continue
	except requests.exceptions.TooManyRedirects as e:
		print ("Too many redirects therefore continuing to next link")
		continue

	page = str(BeautifulSoup(req.content, "lxml"))
	link, end_quote = getLink(page)

	# print (link, end_quote)

	# Checks if more links are present in the page
	while link!=-1:		
		page = page[end_quote:]
		for non in links_unvalid:
			if non in link:
				not_valid_url = 1
				break
		if (not_valid_url == 1):
			not_valid_url = 0
			pass

		# if 'https://' in link:
		# 	continue
		#if ("javascript" in link or "jpg" in link or "png" in link or "jpeg" in link):
		#	pass
		else:
			if ('http://' not in link and 'https://' not in link):
				link = url + link

			link = link.strip(' /') + '/'

			flag = 0

			# Checks for max depth
			if depth+1 > max_depth:
				flag = 1

			# Checks if the link is already present in links_tocrawl list
			for entry in links_tocrawl:
				if link == entry[0]:
					flag = 1

			# Checks if the link is already crawled
			for entry in links_crawled:
				if link == entry[0]:
					flag = 1

			if flag == 0:
				links_tocrawl.append([link, depth+1])

		link, end_quote = getLink(page)
	links_crawled.append([url, depth])
	links_tocrawl.pop(0)
	#print "Tocrawl", len(links_tocrawl)
	#print "Crawled", len(links_crawled)

# f1 = open('virtualtocrawl', 'w')

data_final = []

#Gets the title from each link page
for item in links_crawled:
	url = item[0]
	depth = item[1]
	req = requests.get(url)
	htmltext = BeautifulSoup(req.content, "lxml")
	head = htmltext.find("head")
	
	if head:
		title = head.find("title")
		txt = title.getText()
	else:
		txt = "Not Found"

	row = [url, txt, depth]
	data_final.append(row)

# Writes the result to a csv file
# with open('./crawled.csv', 'w') as file:
# 	writer = csv.writer(file, delimiter=",")
# 	for row in data_final:
# 		writer.writerow(row)

# for link in links_tocrawl:
# 	f1.write(link)
# 	f1.write('\n')

for link in data_final:
	link[1] = re.sub("\n","",link[1])
	link[1] = re.sub(" ","",link[1])
	if link[1]:
		print(link[1])
		
# Writes the result to a txt file 
# f1 = open('crawled.txt', 'w')
# for link in data_final:
# 	f1.write("URL: "+ str(link[0]) +" title: " + str(link[1]) +" depth: " + str(link[2]))
# 	f1.write('\n')
# f1.close()


# f2.close()
#print "Tocrawl", links_tocrawl
#print "Crawled", links_crawled
#print "Broken link", links_broken
#print "Crawled unvalid links", crawled_unvalid_links

############################################################################################
# grabPage.py
#
#
# Author: Aamir Zainulabdeen
#
# Group: COS 333: Eric Hayes '18, Emily Tang '18, Fabian Lindfield Roberts '18
############################################################################################

# dependencies 
import sys
import requests as req
from bs4 import BeautifulSoup
import re # for the date, homeboy
import json
import time

# globl var defining date syntax for daily princetonian
dateRE = '''(Jan |Feb |Mar |Apr |May |Jun |Jul |Aug |Sep |Oct |Nov |Dec )([1-9]|[12][0-9]|[3][01]), [2-9][0-9][0-9][0-9]'''

# globl vars defining the section URL structure
baseSectionURL = "http://www.dailyprincetonian.com/section/"
sections = ["news", "opinion", "sports", "street", "multimedia", "blog/intersections", "special", "editorial"]


"""
Output depends on switch. The default output is an encoded JSON string with 
article title, date, author, and body (with the paragraphs joined by newlines
as defined in getBodyAsString(). If swtich is anyting else, the output is a list
with one dict containing the page (for testing purposes).
"""
def jsonify_page(url, switch="JSON"):
    # download the page                                                                                                                                    
    soup = getSoup(url)
    # set all page contents                                                                                                                                           
    title = getTitle(soup)[0].text
    author = getAuthor(soup)[0].text
    date = getDate(soup)
    # body comes in list of paragraphs                                                                                                                                
    body = grabPageText(soup)
    body = getBodyAsString(body)
    # now convert to json dict
    bornAgain = [{'title': title, 'author': author, 'date': date, 'body': body}]
    if switch == "JSON":
        return json.dumps(bornAgain)
    else:
        return bornAgain

# utility testing
def testUrl(testUrl):
    # only download the page once
    soup = getSoup(testUrl)

    # get the article title, time, author
    title = getTitle(soup)
    sys.stdout.write("Title:\t\t")
    sys.stdout.write(title[0].text)
    writeN()
    
    author = getAuthor(soup)
    sys.stdout.write("Author:\t\t")
    sys.stdout.write(author[0].text)
    
    date = getDate(soup)
    sys.stdout.write("\t\tDate:\t\t")
    sys.stdout.write(date)
    writeN()
    
    # get the body text of our soup
    body = grabPageText(soup)    
    # print out the article body
    for p in body:
        sys.stdout.write(p.text)
        writeN()

def getBodyAsString(body):
    out = ""
    for p in body:
        out = out + p.text + "\n\n"
    return(out)

def main():
    testUrls = ["http://www.dailyprincetonian.com/article/2017/03/u-alum-organization-focuses-on-new-energy-sources",
                "http://www.dailyprincetonian.com/article/2017/03/editorial-affirming-free-speech-and-encouraging-team-leadership",
                "http://www.dailyprincetonian.com/article/2017/03/weber-talks-media-at-social-day"]

    for url in testUrls:
        testUrl(url)
        writeBreak()

# write break between articles
def writeBreak():
    sys.stdout.write('''\n\n
________________________________________________________________________________________
\n\n''')

# write newlines
def writeN():
    sys.stdout.write("\n\n")
    return

# download the page 
def getSoup(pageURL):
    page = req.get(pageURL)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

# grab the article title
def getTitle(soup):
    title = soup.select(".headline")
    return title

# grab the article author
def getAuthor(soup):
    author = soup.select(".author-line > a")
    return author

def getDate(soup):
    date = soup.select(".author")
    found = re.search(dateRE, date[0].text)
    return found.group(0)

# returns a list representation of a page's article body
def grabPageText(soup):
    # a list that contains all of the paragraphs in an article
    body = soup.select(".article-copy > p")
    return body


# return a list of all article URLS from a query page
# params is a list of length three, the first element is
# the fromDate, second is toDate, third is query type
# dates are in the string format "mm/dd/yyyy"
# type is one of these possible strings: "article"; "media"; "post"
def getArticleURLS(params):
    qURL = getPrinceQURL(params[0], params[1], params[2])
    soup = getSoup(qURL)
    links = soup.select(".clearfix a")
    urls = list()
    baseURL = "http://www.dailyprincetonian.com"
    # links are repeated, so we only select even indexes
    for i in range(0, len(links), 2):
        urls.append(links[i]['href'])

    for i in range(0, len(urls)):
        urls[i] = baseURL + urls[i]

    return urls

# construct a dated query string for articles
# a QURL is a query URL 
# dates are in the string format "mm/dd/yyyy"
# type is one of these possible strings: "article"; "media"; "post"
def getPrinceQURL(fromDate, toDate, type):
    fromMonth, fromDay, fromYear = fromDate.split("/")
    toMonth, toDay, toYear = toDate.split("/")

    # query string params
    baseURL = "http://www.dailyprincetonian.com/search/"
    fromMonthBase = "?a=1&s=&ti=&ts_month="
    fromDayBase = "&ts_day="
    fromYearBase = "&ts_year="
    toMonthBase = "&te_month="
    toDayBase = "&te_day="
    toYearBase = "&te_year="
    typeBase = "&au=&tg=&ty="
    endURL = "&o=date"

    construction = baseURL + fromMonthBase + fromMonth 
    construction = construction + fromDayBase + fromDay 
    construction = construction + fromYearBase + fromYear + toMonthBase
    construction = construction + toMonth + toDayBase + toDay
    construction = construction + toYearBase + toYear + typeBase + type + endURL

    return construction

# get today's articles in a list of JSON's using the time module
def getTodaysArticles():
    today = time.strftime("%m/%d/%Y")
    # get today's articles 
    urls = getArticleURLS([today, today, "article"])
    outputJSON = list()
    for url in urls:
        outputJSON.append(jsonify_page(url))

    return outputJSON

# get a specific date's articles as a list of JSONS
def getDatesArticles(date):
    # get today's articles 
    urls = getArticleURLS([date, date, "article"])
    outputJSON = list()
    for url in urls:
        outputJSON.append(jsonify_page(url))

    return outputJSON


# run main
if __name__ == "__main__":
    main()

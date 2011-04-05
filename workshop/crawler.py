"""Simple web search engine - this file contains version for the workshop."""

import BeautifulSoup
import re
import urllib2
import urlparse
import sys

"""Complied regex used to identify words."""
SPLITTER = re.compile('\\W*')
"""List of words to ignore."""
STOP_WORDS = {'the':1, 'of':1, 'to':1, 'and':1, 'a':1, 'in':1, 'is':1, 'it':1}
"""List of html tags to ignore."""
STOP_TAGS = ['script', 'style']

class RawTextCrawler(object):

  def __init__(self):
    self.url_title_text = []

  def GetTextOnly(self, soup):
    """Extract pure text content from an HTML soup."""
    if soup.string == None:
      result_text = ''
      for content in soup.contents:
        sub_text = self.GetTextOnly(content)
        result_text += sub_text + '\n'
      return result_text
    elif not hasattr(soup, 'name') or soup.name not in STOP_TAGS:
      return soup.string.strip()
    return ''

  def SeparateWords(self, text):
    """Separate the words in text."""
    # NOTE(cbrumm): Stemming could be added here.
    return [word.lower() for word in SPLITTER.split(text) if word != '']

  def IsIndexed(self, url):
    """Returns true if this url is already indexed."""
    return False

  def AddUrlAndText(self, url, html_soup):
    if html_soup('title'):
      title = html_soup('title')[0].string
    else:
      title = ''
    words = self.SeparateWords(self.GetTextOnly(html_soup))
    words = filter(lambda w: w not in STOP_WORDS, words)
    self.url_title_text.append((url, title, reduce(lambda w1,w2: w1 + ' ' + w2, words, '')))

  def DumpUrlAndText(self):
    print len(self.url_title_text)
    for url, title, text in self.url_title_text:
      print url
      print title
      print text

  def Crawl(self, pages, depth=2):
    """Crawl the passed list of pages using BFS to the passed depth."""
    for i in range(depth):
      new_pages = set()
      for page in pages:
        # Crawl one page.
        try:
          connection = urllib2.urlopen(page)
        except urllib2.URLError:
          sys.stderr.write('[urllib2.URLError] Could not open %s\n' % page)
          continue
        except:
          sys.stderr.write('Unexpected error: %s\n' % sys.exc_info()[0])
          continue
        html_soup = BeautifulSoup.BeautifulSoup(connection.read())
        self.AddUrlAndText(page, html_soup)
        # Follow links.
        links = html_soup('a')
        for link in links:
          if ('href' in dict(link.attrs)):
            url = urlparse.urljoin(page, link['href'])
            if url.find("'") != -1:
              continue
            url = url.split('#')[0]
            if url[0:4] == 'http' and not self.IsIndexed(url):
              new_pages.add(url)
      # Go on with new pages.
      pages = new_pages


def AcceptQueries():
  try:
    query = raw_input()
    while query:
      print query
      query = raw_input()
    print
  except EOFError:
    print

def __main__():
  page_list = ['http://www.dmoz.org/', 'http://dir.yahoo.com/']
  crawler = RawTextCrawler()
  crawler.Crawl(page_list, 1)
  crawler.DumpUrlAndText()
  AcceptQueries()

if __name__ == '__main__':
  __main__()

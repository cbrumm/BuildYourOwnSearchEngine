"""Simple web search engine - this file contains version for the workshop."""

import BeautifulSoup
import re
import urllib2
import urlparse

"""Complied regex used to identify words."""
SPLITTER = re.compile('\\W*')
"""List of words to ignore."""
STOP_WORDS = {'the':1, 'of':1, 'to':1, 'and':1, 'a':1, 'in':1, 'is':1, 'it':1}

class RawTextCrawler(object):

  def __init__(self):
    self.url_and_text = []

  def GetTextOnly(self, soup):
    """Extract pure text content from an HTML soup."""
    if soup.string == None:
      result_text = ''
      for content in soup.contents:
        sub_text = self.GetTextOnly(content)
        result_text += sub_text + '\n'
      return result_text
    else:
      return soup.string.strip()

  def SeparateWords(self, text):
    """Separate the words in text."""
    # NOTE(cbrumm): Stemming could be added here.
    return [word.lower() for word in SPLITTER.split(text) if word != '']

  def IsIndexed(self, url):
    """Returns true if this url is already indexed."""
    return False

  def AddUrlAndText(self, url, html_soup):
    words = self.SeparateWords(self.GetTextOnly(html_soup))
    words = filter(lambda w: w not in STOP_WORDS, words)
    self.url_and_text.append((url, reduce(lambda w1,w2: w1 + ' ' + w2, words, '')))

  def DumpUrlAndText(self):
    print len(self.url_and_text)
    for url, text in self.url_and_text:
      print url
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
          print 'Could not open %s' % page
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

def __main__():
  page_list = ['http://www.dmoz.org/', 'http://dir.yahoo.com/']
  crawler = RawTextCrawler()
  crawler.Crawl(page_list, 1)
  crawler.DumpUrlAndText()

if __name__ == '__main__':
  __main__()

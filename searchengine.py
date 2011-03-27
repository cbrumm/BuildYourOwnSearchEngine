"""
Simple web search engine - this file contains crawler and index.

Heavily inspired by chapter 4 of the excellent 'Programming Collective
Intelligence' by Toby Segaran (O'Reilly).

This example uses open source software to get the job done:

(1) BeautifulSoup to do the dirtly html parsing.
http://www.crummy.com/software/BeautifulSoup/
(2) Pysqlite for storing the index in a relational database on disk.
http://code.google.com/p/pysqlite/
"""

import BeautifulSoup
import urllib2
import urlparse

STOP_WORDS = {'the':1, 'of':1, 'to':1, 'and':1, 'a':1, 'in':1, 'is':1, 'it':1}

class Crawler(object):

  def __init__(self, db_name):
    pass

  def __del__(self):
    pass

  def DbCommit(self):
    """Commit the current crawl to the database backend."""

  def GetEntryId(self, table, field, value, create_new=True):
    """Get an entry id and add it if it's not present."""

  def AddToIndex(self, url, soup):
    """Index an individual page."""
    print 'Indexing %s' % url

  def GetTextOnly(self, soup):
    """Extract pure text content from an HTML page."""

  def SeparateWords(self, text):
    """Separate the words in text."""

  def IsIndexed(self, url):
    """Returns true if this url is already indexed."""
    return False

  def AddLinkRef(self, urlFrom, urlTo, linkText):
    """Add a link between two urls."""

  def Crawl(self, pages, depth=2):
    """Crawl the passed list of pages using BFS to a depth of 2."""
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
        self.AddToIndex(page, html_soup)
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
            link_text = self.GetTextOnly(link)
            self.AddLinkRef(page, url, link_text)
        # Add page to persistent index.
        self.DbCommit()
      # Go on with new pages.
      pages = new_pages

  def CreateIndexTables(self):
    """Create the necessary backend database tables."""

def __main__():
  page_list = ['http://kiwitobes.com/wiki/Perl.html', 'http://www.google.com',
               'http://www.yahoo.com']
  crawler = Crawler('')
  crawler.Crawl(page_list)

__main__()

"""Simple web search engine - this file contains crawler and index."""

import BeautifulSoup
from pysqlite2 import dbapi2
import re
import urllib2
import urlparse
import sys

"""Complied regex used to identify words."""
SPLITTER = re.compile('\\W*')
"""List of words to ignore."""
STOP_WORDS = {'the':1, 'of':1, 'to':1, 'and':1, 'a':1, 'in':1, 'is':1, 'it':1}

class Crawler(object):

  def __init__(self, db_name):
    self.db_connection = dbapi2.connect(db_name)

  def __del__(self):
    self.db_connection.close()

  def DbCommit(self):
    """Commit the current index to the database backend."""
    self.db_connection.commit()

  def GetEntryId(self, table, field, value, create_new=True):
    """Get an entry id - add it if it's not present."""
    cursor = self.db_connection.execute("select rowid from %s where "
      "%s='%s'" % (table, field, value))
    result = cursor.fetchone()
    if result == None:
      cursor = self.db_connection.execute("insert into %s (%s) values "
        "('%s')" % (table, field, value))
      return cursor.lastrowid
    else:
      return result[0]

  def AddToIndex(self, url, soup):
    """Index an individual page."""
    if self.IsIndexed(url):
      return
    print 'Indexing %s' % url
    words = self.SeparateWords(self.GetTextOnly(soup))
    url_id = self.GetEntryId('urllist', 'url', url)
    # Link each word to its url
    for position in range(len(words)):
      word = words[position]
      if word in STOP_WORDS:
        continue
      word_id = self.GetEntryId('wordlist', 'word', word)
      self.db_connection.execute('insert into wordlocation(urlid, wordid, '
        'location) values (%d, %d, %d)' % (url_id, word_id, position))

  def GetTextOnly(self, soup):
    """Extract pure text content from an HTML page."""
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
    url_id = self.db_connection.execute("select rowid from urllist where "
      "url='%s'" % url).fetchone()
    if url_id != None:
      # Check if the url was actually crawled.
      word_locations = self.db_connection.execute('select * from wordlocation '
        'where urlid=%d' % url_id[0]).fetchone()
      if word_locations != None:
        return True
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
    self.db_connection.execute('create table urllist(url)')
    self.db_connection.execute('create table wordlist(word)')
    self.db_connection.execute('create table wordlocation '
      '(urlid,wordid,location)')
    self.db_connection.execute('create table link(fromid integer,toid integer)')
    self.db_connection.execute('create table linkwords(wordid,linkid)')
    self.db_connection.execute('create index wordidx on wordlist(word)')
    self.db_connection.execute('create index urlidx on urllist(url)')
    self.db_connection.execute('create index wordurlidx on '
      'wordlocation(wordid)')
    self.db_connection.execute('create index urltoidx on link(toid)')
    self.db_connection.execute('create index urlfromidx on link(fromid)')
    self.DbCommit()

def __main__():
  page_list = ['http://www.wikipedia.org/', 'http://www.dmoz.org/']
  crawler = Crawler('searchindex.db')
  crawler.CreateIndexTables()
  crawler.Crawl(page_list, 1)

if __name__ == '__main__':
  __main__()

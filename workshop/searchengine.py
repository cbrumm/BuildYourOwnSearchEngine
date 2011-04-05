"""Simple search engine - this file contains version for the workshop."""

class SearchEngine(object):

  class Entry:
    def __init__(self):
      self.title_indexes = []
      self.text_indexes = []

    def __repr__(self):
      return 'Entry.title_indexes : %s, Entry.text_indexes : %s' % (str(self.title_indexes), str(self.text_indexes))


  def __init__(self):
    self.index = {}  # url -> (title, [word])
    self.inverted_index = {}  # word -> url -> Entry

  def AddToInvertedIndex(self, url, word, word_index, in_title = False):
    if word not in self.inverted_index:
      self.inverted_index[word] = {}
    if url not in self.inverted_index[word]:
      self.inverted_index[word][url] = SearchEngine.Entry()
    entry = self.inverted_index[word][url]
    if in_title:
      entry.title_indexes.append(word_index)
    else:
      entry.text_indexes.append(word_index)

  def FillInvertedIndex(self):
    """Fills inverted index from index"""
    for url in self.index.keys():
      for title_index, title_word in enumerate(self.index[url][0]):
        self.AddToInvertedIndex(url, title_word, title_index, in_title = True)
      for text_index, text_word in enumerate(self.index[url][1]):
        self.AddToInvertedIndex(url, text_word, text_index, in_title = False)

  def ReadIndexFromStdin(self):
    """Read from stdin into indexes"""
    try:
      count = int(raw_input())
      for i in range(count):
        url = raw_input()
        title = raw_input()
        text = raw_input().split()  # list of words
        self.index[url] = (title, text)
    except EOFError:
      print 'Failed reading index from stdin'
      raise
    self.FillInvertedIndex()

  def ExecuteQuery(self, query):
    words = query.split()
    try:
      urls = set(self.inverted_index[words[0]].keys())
      for i in range(1, len(words)):
        word = words[i]
        urls = urls.intersection(self.inverted_index[word].keys())
      return urls
    except KeyError:
      return set()

  def AcceptQueries(self):
    try:
      query = raw_input()
      while query:
        print query
        results = self.ExecuteQuery(query)
        print results
        query = raw_input()
      print
    except EOFError:
      print

def __main__():
  search = SearchEngine()
  search.ReadIndexFromStdin()
#  print search.index
#  print search.inverted_index
  search.AcceptQueries()

if __name__ == '__main__':
  __main__()

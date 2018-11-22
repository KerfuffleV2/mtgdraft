#!/usr/bin/env python3

from html.parser import HTMLParser

import urllib
import urllib.request
import urllib.error
import csv
import operator

class MTGTLParser(HTMLParser):
  def __init__(self, *args, **kwargs):
    self.result = {}
    self.snarf = None
    super().__init__(*args, **kwargs)

  def handle_starttag(self, tag, attrs):
    ad = dict(attrs)
    if self.snarf is None:
      if tag == 'div' and ad.get('class') == 'hidden_card':
        self.snarf = {}

  def handle_endtag(self, tag):
    if tag == 'a':
      self.snarf = None

  def handle_data(self, data):
    data = data.strip()
    if not data:
      return
    if self.snarf is None:
      return
    snarf = self.snarf
    if 'rating' not in snarf:
      snarf['rating'] = data.split('//', 1)[0].strip()
    elif 'name' not in snarf:
      snarf['name'] = data
    elif 'desc' not in snarf:
      snarf['desc'] = data
      if snarf['name'] in self.result:
        print('COLLISION', snarf['name'])
      else:
        self.result[snarf['name']] = snarf
        self.snarf = None


def main():
  result = {}
  mtgsets = ('guilds-of-ravnica', 'core-set-2019', 'dominaria', 'rivals-of-ixalan', 'ixalan')
  for mtgset in mtgsets:
    uri = 'https://www.mtgranks.com/set/{0}/'.format(mtgset)
    print('Fetching', uri)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    ua = 'MTGDraftHelper+urllib'
    req = urllib.request.Request(uri, headers = {'User-Agent': ua })
    resp = opener.open(req)
    data = resp.read()
    parser = MTGTLParser()
    parser.feed(data.decode('utf-8'))
    result = { **result, **parser.result }
  with open('mtgtier.csv', 'w') as outfp:
    cw = csv.writer(outfp, quoting = csv.QUOTE_NONNUMERIC)
    for row in result.values():
      cw.writerow((row['name'], row['rating'], row['desc']))


main()

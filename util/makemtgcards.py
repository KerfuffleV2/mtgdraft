#!/usr/bin/env python3

import json
import string
import csv
import sys

_fcconversions = (('convertedManaCost', 'cost'), ('name', 'name'), ('text', 'text'), ('manaCost', 'colors'), ('multiverseId', 'cardid'), ('rarity', 'rarity'), ('types', 'types'))
#, ('subtypes', 'subtypes'), ('supertypes', 'supertypes'))

def fromFullCard(fc):
  card = {}
  for f,t in _fcconversions:
    v = fc.get(f)
    if v is None:
      continue
    card[t] = v
  return card


def fixType(c):
  typs = tuple(t.lower() for t in c['types'])
  typ = None
  if 'instant' in typs:
    typ = 'Fast Spell'
  elif 'sorcery' in typs:
    typ = 'Spell'
  elif 'enchantment' in typs or 'planeswalker' in typs:
    typ = 'Attachment'
  elif 'artifact' in typs and c.get('subtype') == 'Equipment':
    typ = 'Attachment'
  elif 'creature' in typs:
    typ = 'Unit'
  elif 'artifact' in typs:
    typ = 'Attachment'
  elif 'land' in typs:
    typ = 'Power'
  elif 'plane' in typs:
    typ = 'Attachment'
  elif 'hero' in typs:
    typ = 'Attachment'
  elif 'scheme' in typs:
    typ = 'Attachment'
  elif 'conspiracy' in typs:
    typ = 'Attachment'
  elif 'vanguard' in typs:
    typ = 'Attachment'
  elif 'phenomenon' in typs:
    typ = 'Attachment'
  elif 'summon' in typs:
    typ = 'Unit'
  elif 'eaturecray' in typs:
    typ = 'Unit'
  else:
    typ = 'Other'
  c['type'] = typ


def hasReqFields(card):
  reqfields = ('rarity', 'convertedManaCost', 'type', 'types', 'name')
  for reqfield in reqfields:
    if reqfield not in card:
      print('ACK', reqfield, card)
      print()
      return False
  return True


def main():
  if len(sys.argv) == 2:
    fn = sys.argv[1]
  else:
    fn = 'AllSets.json'
  with open(fn, 'r', encoding = 'utf-8') as fp:
    jresult = json.load(fp)
  result = {}
  for mtgsetname in ('M19', 'DOM', 'RIX', 'XLN', 'GRN'):
    mtgset = jresult[mtgsetname]
    for fullcard in mtgset['cards']:
      #print(fullcard)
      if fullcard['type'] in ('Card', ''):
        continue
      if not hasReqFields(fullcard):
        continue
      if 'text' not in fullcard:
        fullcard['text'] = fullcard['type']
      card = fromFullCard(fullcard)
      if card['cost'] != float(int(card['cost'])):
        continue
      card['cost'] = int(card['cost'])
      fixType(card)
      # fixColors(card)
      card['text'] = card['text'].replace('\n', ' ')
      result[card['name']] = card
  with open('mtgcards.csv', 'w') as outfp:
    cw = csv.writer(outfp, quoting = csv.QUOTE_NONNUMERIC)
    for row in result.values():
      if 'colors' not in row:
        continue
      cw.writerow((row['name'], row['cost'], row['rarity'], row['type'], row['colors'], row['text']))


if __name__ == '__main__':
  main()
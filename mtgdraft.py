#!/usr/bin/env python3

import readline
import csv
import itertools
import textwrap
import shutil
import sys
import string
from mtgdraft import styling
from mtgdraft.styling import cf, mkRatingColor, TYPECOLORS, RARITYCOLORS, COLORCOLORS


CARDSFN = 'mtgcards.csv'
TIERLISTFN = 'mtgtier.csv'

WIDTH = lambda: shutil.get_terminal_size((80,25)).columns - 4


def mkRatingString(rating):
  if rating is None:
    return '?.??'
  if not isinstance(rating, float):
    return rating
  return '{0:1.2f}'.format(rating)


def prettyColors(s):
  cparts = tuple(tuple(s[:-1].split('/')) for s in s.split('{') if s)
  result = []
  for cp in cparts:
    subparts = []
    for scp in cp:
      if scp.isdigit() or scp == 'X':
        subparts.append(cf('{r}{fwhite}{neutralcost}', neutralcost = scp))
      else:
        subparts.append(cf('{r}{color}{colorchar}', color = COLORCOLORS[scp], colorchar = scp))
    if len(subparts) == 1:
      result.append(subparts[0])
    else:
      result.append(cf('{r}{d}<{subparts}{r}{d}>', subparts = cf('{r}{d}/{r}').join(subparts)))
  return ''.join(result)


class Card(object):
  def __init__(self, name, cost, rarity, ctype, colors, text):
    self.name = name
    self.cost = cost
    self.rarity = rarity
    self.type = ctype
    self.colors = colors
    self.text = text

  def pretty(self):
    rletter = self.rarity[0].upper()
    return cf('{r}{rcolor}{rletter}{r}{d}:{r}{tcolor}{name}{r}{d}({fwhite}{cost}{r}{d}:{r}{colors}{r}{d})',
      rcolor = RARITYCOLORS[rletter], rletter = rletter, tcolor = TYPECOLORS[self.type],
      name = self.name, cost = self.cost, colors = prettyColors(self.colors))


class Cards(object):
  def __init__(self):
    self.cards = {}

  def load(self, fn):
    cards = self.cards
    with open(fn, 'r', encoding = 'utf-8') as fp:
      cfp = csv.reader(fp)
      for name, cost, rarity, ctype, colors, text in cfp:
        cost = int(cost)
        fixedname = name.replace('-', ' ').lower()
        card = Card(name, cost, rarity, ctype, colors, text)
        cards[fixedname] = card


class RatedCard(object):
  def __init__(self, name, rating, text, card = None):
    self.name = name
    self.rating = rating
    self.text = text
    self.card = card

  def prettyCard(self):
    card = self.card
    if not card:
      return self.name
    if isinstance(card, tuple):
      return ' // '.join(c.pretty() for c in card)
    return card.pretty()

  def pretty(self):
    c = self
    ctext = '^^^ {text}'.format(text = textwrap.TextWrapper(width = WIDTH(), subsequent_indent = '    ').fill(c.text))
    ratingcol = mkRatingColor(c.rating)
    cardstr = self.prettyCard()
    output = cf('{ratingcol}{ratingstr:<5}{r}{fwhite}{b}{cardstr}\n{r}{text}',
      ratingstr = mkRatingString(c.rating) if c.rating >= 0 else '',
      cardstr = cardstr, ratingcol = ratingcol,
      text = ctext)
    return output


class RatedCards(object):
  def __init__(self):
    self.cards = {}

  def load(self, fn, cards = None):
    rcards = self.cards
    with open(fn, 'r', encoding = 'utf-8') as fp:
      cfp = csv.reader(fp)
      for name,rating,text in cfp:
        # Note: The tier list data doesn't preserve the dashes in card names.
        name = name.replace('-', ' ')
        lcname = name.lower()
        rating = float(rating.split('-', 1)[0].split(':', 1)[0])
        if cards is not None:
          card = cards.get(lcname)
          if card is None:
            nameparts = lcname.split(None)
            if len(nameparts) == 2:
              dualcard1 = cards.get(nameparts[0])
              dualcard2 = cards.get(nameparts[1])
              if dualcard1 and dualcard2:
                card = (dualcard1, dualcard2)
          # if card is None:
          #   print('Not found:', name, card)
        else:
          card = None
        rcards[name] = RatedCard(name, float(rating), text, card = card)


def showRatingList(deckcards, extratext = True, padding = ''):
  ratingf = lambda dcard: dcard.rating
  srl = sorted(deckcards.values(), key = ratingf, reverse = True)
  gsrl = itertools.groupby(srl, ratingf)
  showncount = 0
  def mkcardtext(deckcard):
    ctext = textwrap.TextWrapper(width = WIDTH(), initial_indent = ' ' * 7, subsequent_indent = ' ' * 7).fill(deckcard.text)
    cardstr = deckcard.prettyCard()
    return cf('{fwhite}{b}{cardstr}{r}{d}:{r}\n{text}', cardstr = cardstr, text = ctext)
  print()
  for rating,g in gsrl:
    if rating < 0:
      rating = '?.??'
    g = list(g)
    shownchunk = 0
    for i in range(0, len(g), 1):
      cardschunk = g[i:i + 1]
      showncount += sum(1 for card in cardschunk)
      if not cardschunk:
        continue
      shownchunk += 1
      items = ' | '.join(mkcardtext(deckcard) for deckcard in cardschunk)
      if shownchunk == 1:
        ratingstr = mkRatingString(rating)
        ratingcol = mkRatingColor(rating)
      else:
        ratingstr = ''
        ratingcol = ''
      print(cf('{padding}{ratingcol}{ratingstr:<5}{r}{items}',
         ratingstr = ratingstr, items = items, ratingcol = ratingcol, padding = padding))
  if extratext:
    print()
  return showncount



def handleDraft():
  try:
    mtgcards = Cards()
    mtgcards.load(CARDSFN)
    mtgcardsdict = mtgcards.cards
  except IOError:
    print('* Note: Could not load {0} so color/cost information will not be available.\n'.format(CARDSFN), file = sys.stderr)
    mtgcardsdict = None
  rcards = RatedCards()
  try:
    rcards.load(TIERLISTFN, cards = mtgcardsdict)
  except IOError:
    print('Error: ')
  cards = rcards.cards
  lccards = dict((k.lower(),k) for k in cards.keys())
  lckeys = list(lccards.keys())

  if readline is not None:
    ckeys = cards.keys()
    def rlcompleterf(line, state):
      if not line:
        result = [c for c in ckeys][state]
      else:
        result = [c for c in ckeys if c.lower().startswith(line.lower())][state]
      return result

    readline.parse_and_bind('tab: complete')
    readline.set_completer_delims('')
    readline.set_completer(rlcompleterf)

  deck = {}
  def findmatches(s):
    return list(k for k in lckeys if k.find(s) != -1)

  while True:
    try:
      line = input('\nEnter card: ')
    except EOFError:
      print('')
      break
    if line is None:
      break
    line = line.strip()
    if line == '':
      showRatingList(deck)
      if deck:
        print('** Starting new set **')
      deck = {}
      continue
    if line[0] == '#':
      continue
    line = line.replace('-' , ' ')
    matches = findmatches(line.lower())
    if not matches:
      print('Unknown', line)
      continue
    elif len(matches) > 1:
      if line not in cards:
        print('\nAmbiguous:', '; '.join(lccards[n] for n in matches))
        print('Enter complete name with capitalization for an exact match.')
        continue
      lccardname = line.lower()
    else:
      lccardname = matches[0]
    cardname = lccards.get(lccardname)
    if cardname is None:
      print('Unknown:', line)
      continue
    deckcard = cards[cardname]
    print(deckcard.pretty())
    deck[cardname] = deckcard
  showRatingList(deck)


def main():
  handleDraft()

main()
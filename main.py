from time import sleep
import os
import random
from rich.style import StyleType

from rich.traceback import install
from rich.console import Console

import _banners

# rich traceback
# install()
con = Console()

dSpielerNamen = {
  1: 'Flora',
  2: 'Mathea',
  3: 'Lutz',
  4: 'Hannah'
}

bClearscreen = True
field_free = '.'
field_hole = ':hole:'
field_target = ':carrot:'
sClick = 'KLICK'
num_of_ones = 24
num_of_twos = 8
num_of_threes = 4
num_of_clicks = 12
num_of_positions = 28
num_of_pieces_per_player = 1  # int(input('Wieviele Spielfiguren pro Spieler?:\t'))

lones = [1] * num_of_ones
ltwos = [2] * num_of_twos
lthrees = [3] * num_of_threes
lclicks = [sClick] * num_of_clicks
lDeck_of_cards = []

lHoles = [13, 25, 16, 23, 4, 21, 7, 19, 10, None]
dBoard = dict(zip(range(1, num_of_positions + 1), [field_free] * num_of_positions))
dBoard[num_of_positions] = field_target

dColors = {
  1: {'text': '[blue]', 'desc': '[bold][blue]BLAU[/]', 'taken': None},
  2: {'text': '[red]', 'desc': '[bold][red]ROT[/]', 'taken': None},
  3: {'text': '[green]', 'desc': '[bold][green]GRÜN[/]', 'taken': None},
  4: {'text': '[yellow]', 'desc': '[bold][yellow]GELB[/]', 'taken': None},
  5: {'text': '[magenta]', 'desc': '[bold][magenta]MAGENTA[/]', 'taken': None},
}

# Start
num_of_players = 2  # int(input('Wieviele Spieler?:\t'))


def pick_card():
  global lDeck_of_cards
  if len(lDeck_of_cards) == 0:
    lDeck_of_cards = lones + ltwos + lthrees + lclicks
  karte = random.choice(lDeck_of_cards)
  lDeck_of_cards.remove(karte)
  return karte, lDeck_of_cards


def click():
  for h in lHoles:
    yield h


def clicked(hole: int):
  global holes
  con.print(f'[blue]{sClick}!', end="")
  last_hole = hole
  hole = next(holes)
  # Liste der Löcher aufgebraucht?
  if hole is None:
    # resetten
    holes = click()
    hole = next(holes)
  con.print(f' -> [yellow]-{hole}-')
  if last_hole:
    dBoard[last_hole] = field_free
  if dBoard[hole] != field_free:
    iPlayer_on_hole = dBoard[hole]
    sName = dPlayers[iPlayer_on_hole]['name']
    sColor = dPlayers[iPlayer_on_hole]['color']
    con.print(f'\nOh NEIN!! Spieler {sColor}{sName}[/] fällt durch das Loch...')
    con.print(f'[red]{_banners.sHole}')
    dPlayers[iPlayer_on_hole]['positionen'][0] = 0
    # input('weiter...')
  dBoard[hole] = field_hole
  return dBoard, hole


def get_next_player(current: int):  # , max_players: int):
  next_player = current + 1
  if next_player > num_of_players:
    next_player = 1
  return next_player


def new_player(iPlayer: int):
  return False, 0


def print_pieces(iPlayer):
  lPieces = dPlayers[iPlayer]['positionen']
  for idx, iField in enumerate(lPieces):
    con.print(f'{idx}: eine Spielfigur auf Feld: {iField}')


def get_target_field(iPos, iSteps):
  lNext_20_fields = list(dBoard.values())[iPos:iPos + 20]

  ifields_free = lNext_20_fields[:iSteps].count(field_free)
  ifields_holes = lNext_20_fields[:iSteps].count(field_hole)
  ifields_targets = lNext_20_fields[:iSteps].count(field_target)
  ifields = ifields_free + ifields_holes + ifields_targets
  if (iPos + ifields) >= num_of_positions:
    return num_of_positions

  iMoreSteps = iSteps
  while ifields != iSteps:
    iMoreSteps += 1
    ifields_free = lNext_20_fields[:iMoreSteps].count(field_free)
    ifields_holes = lNext_20_fields[:iMoreSteps].count(field_hole)
    ifields_targets = lNext_20_fields[:iMoreSteps].count(field_target)
    ifields = ifields_free + ifields_holes + ifields_targets

  iResult = iPos + iMoreSteps
  return iResult


def move_player(iPlayer: int, iSteps: int):
  iSetPieces = dPlayers[iPlayer]['set_pieces']

  # first piece
  bFirstPiece = iSetPieces == 0
  bOnePiece = iSetPieces == 1
  bMorePieces = iSetPieces > 1

  # noch keine Figur
  if bFirstPiece:
    iPos = 0
    dPlayers[iPlayer]['set_pieces'] += 1
  # genau eine Figur
  elif bOnePiece:
    iPos = dPlayers[iPlayer]['positionen'][0]
  # mehr als eine Figur
  elif bMorePieces:
    con.print(f'Du hast {iSetPieces} im Spiel:')
    print_pieces(iPlayer)
    iPiece = input('Welche Figur willst du bewegen?\t')
    iPos = dPlayers[iPlayer]['positionen'][iPiece]
  else:
    print('FEHLER')
    iPos = None

  iTarget_field = get_target_field(iPos, iSteps)

  # Endposition erreicht
  if iTarget_field >= num_of_positions:
    dPlayers[iPlayer]['positionen'][0] = num_of_positions
    dBoard[iPos] = field_free
    return True, num_of_positions
  sTarget = dBoard[iTarget_field]

  # Ziel ein Loch
  if sTarget == field_hole:
    sName = dPlayers[iPlayer]['name']
    sColor = dPlayers[iPlayer]['color']
    con.print(f'\nOh NEIN!! Spieler {sColor}{sName}[/] hüpft in das Loch...')
    con.print(f'[red]{_banners.sHole}')
    dPlayers[iPlayer]['positionen'][0] = 0
    input('weiter...')
  # Ziel ist frei
  elif sTarget == field_free:
    dPlayers[iPlayer]['positionen'][0] = iTarget_field

  if iPos != 0:
    dBoard[iPos] = field_free

  return False, iTarget_field


def show_status_board():
  pos = [str(x) for x in dBoard.keys()]
  loads = [str(x) for x in dBoard.values()]
  con.print('\t'.join(pos[:num_of_positions // 3]))
  # con.print('\t'.join(loads[:num_of_positions // 3]))
  for field in loads[:num_of_positions // 3]:
    # Loch
    if field == field_hole:
      con.print(f'{field_hole}', end='\t')
    # free
    elif field == field_free:
      con.print(field_free, end='\t')
    # with player
    else:
      ifield = int(field)
      scolor = dPlayers[ifield]["color"]
      sname = dPlayers[ifield]["name"]
      con.print(f'{scolor}{sname}[/]', end='\t')

  con.print()
  con.print('\t'.join(pos[num_of_positions // 3:(num_of_positions // 3) * 2]))
  # con.print('\t'.join(loads[num_of_positions // 3:(num_of_positions // 3) * 2]))
  for field in loads[num_of_positions // 3:(num_of_positions // 3) * 2]:
    # Loch
    if field == field_hole:
      con.print(f'{field_hole}', end='\t')
    # free
    elif field == field_free:
      con.print(field_free, end='\t')
    # with player
    else:
      ifield = int(field)
      scolor = dPlayers[ifield]["color"]
      sname = dPlayers[ifield]["name"]
      con.print(f'{scolor}{sname}[/]', end='\t')
  con.print()
  con.print('\t'.join(pos[(num_of_positions // 3) * 2:]))
  # con.print('\t'.join(loads[(num_of_positions // 3) * 2:]))
  for field in loads[(num_of_positions // 3) * 2:]:
    # Loch, freies Feld, Karotte
    if field in [field_hole, field_free, field_target]:
      con.print(field, end='\t')
    # with player
    else:
      ifield = int(field)
      scolor = dPlayers[ifield]["color"]
      sname = dPlayers[ifield]["name"]
      con.print(f'{scolor}{sname}[/]', end='\t')
  con.print()


def edit_board():
  for k, v in dPlayers.items():
    # print(f"{v['name']}: {v['positionen']}")
    for pos in v['positionen']:
      if pos:
        dBoard[pos] = k


dPlayers = {}
for i in range(1, num_of_players + 1):
  name = dSpielerNamen[i]  # input(f'Wie heißt Spieler {i}?:\t')
  for k, dic in dColors.items():
    if dic['taken'] is None:
      con.print(f'{k}: {dic["desc"]}')
  iColor = i  # int(input('Welche Farbe?: '))
  dColors[iColor]['taken'] = i
  dPlayers[i] = {
    'name': name,
    'positionen': [0] * num_of_pieces_per_player,
    'color': dColors[iColor]['text'],
    'set_pieces': 0
  }

for k, v in dPlayers.items():
  con.print(f'Spieler {k}:')
  con.print(f"Name: {v['name']} - {v['positionen']}")


holes = click()
iCurr_player = 1
hole = None
dTimeline = {}
iRound = 0

while True:
  # print(dBoard)
  # sleep(2)
  if bClearscreen:
    os.system('cls')
  print("#" * 50)
  print("#" * 50)
  for k, v in dPlayers.items():
    con.print(f'Spieler {k}:')
    con.print(f"Name: {v['name']} - {v['positionen']}")
  if iCurr_player == 1:
    iRound += 1
    dTimeline[iRound] = []
  bWin, iTarget_field = False, None
  sCard = None
  sCurr_player = dPlayers[iCurr_player]['name']
  sColor = dPlayers[iCurr_player]['color']
  edit_board()
  show_status_board()
  con.print(f'{sColor}{sCurr_player.upper()}[/], Du bist dran - ziehe eine Karte!')
  # with con.status(f'{sColor}{sCurr_player}[/] zieht eine Karte....', spinner="dots"):
  #   sleep()
  sCard, lDeck_of_cards = pick_card()

  if sCard == sClick:
    sTurn = f'KLICK! {sColor}{sCurr_player}[/] darf drehen'
    dTimeline[iRound].append(sTurn)
    con.print(sTurn)
    dBoard, hole = clicked(hole)
  else:
    # con.print(f'{sColor}{sCurr_player}[/] darf {sCard} Schritte gehen...')
    # Player already present on board
    if any(dPlayers[iCurr_player]['positionen']):
      if num_of_pieces_per_player > 1:
        sNew = input('[N]eue Figur oder [B]ewegen?\t')[0].lower()
        if sNew == 'n':
          bWin, iTarget_field = new_player(iCurr_player, sCard)
          sTurn = f'{sColor}{sCurr_player}[/] setzt eine weitere Figur auf {iTarget_field}.'
          dTimeline[iRound].append(sTurn)
        else:
          bWin, iTarget_field = move_player(iCurr_player, sCard)
          sTurn = f'{sColor}{sCurr_player}[/] darf {sCard} Schritte gehen und landet auf {iTarget_field}.'
          dTimeline[iRound].append(sTurn)
          if bWin:
            con.print(f'[yellow]{_banners.sWinner}')
            sTurn = f'YEEAAHH!!!!! {sColor}{sCurr_player}[/] hat gewonnen!!'
            con.print(sTurn)
            dTimeline[iRound].append(sTurn)
      else:
        bWin, iTarget_field = move_player(iCurr_player, sCard)
        sTurn = f'{sColor}{sCurr_player}[/] darf {sCard} Schritte gehen und landet auf {iTarget_field}.'
        dTimeline[iRound].append(sTurn)
        if bWin:
          con.print(f'[yellow]{_banners.sWinner}')
          sTurn = f'YEEAAHH!!!!! {sColor}{sCurr_player}[/] hat gewonnen!!'
          dTimeline[iRound].append(sTurn)
    else:
      # Place first player on board
      bWin, iTarget_field = move_player(iCurr_player, sCard)
      sTurn = f'{sColor}{sCurr_player}[/] setzt die erste Figur auf {sCard}'

    con.print(sTurn)

  if bWin:
    break
  iCurr_player = get_next_player(iCurr_player)

input('Ablauf...')
for round, sDesc in dTimeline.items():
  con.print(f'\n[yellow]######### Runde {round} #########')
  con.print(sDesc)

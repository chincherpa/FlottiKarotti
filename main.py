from time import sleep
import os
from collections import defaultdict
import random
from rich.style import StyleType

from rich.traceback import install
from rich.console import Console

install()
con = Console()

dSpielerNamen = {
  1: 'Flora',
  2: 'Mathea',
  3: 'Lutz',
  4: 'Hannah'
}

bClearscreen = False
field_free = '.'
field_hole = ':hole:'
sClick = 'KLICK'
num_of_ones = 24
num_of_twos = 8
num_of_threes = 4
num_of_clicks = 20  # 12
num_of_positions = 25  # 28

lones = [1] * num_of_ones
ltwos = [2] * num_of_twos
lthrees = [3] * num_of_threes
lclicks = [sClick] * num_of_clicks
lDeck_of_cards = []

lHoles = [13, 25, 16, 23, 4, 21, 7, 19, 10, None]
dBoard = dict(zip(range(1, num_of_positions + 1), [field_free] * num_of_positions))

dColors = {
  1: {'text': '[blue]', 'desc': '[bold][blue]BLAU[/]', 'taken': None},
  2: {'text': '[red]', 'desc': '[bold][red]ROT[/]', 'taken': None},
  3: {'text': '[green]', 'desc': '[bold][green]GRÜN[/]', 'taken': None},
  4: {'text': '[yellow]', 'desc': '[bold][yellow]GELB[/]', 'taken': None},
  5: {'text': '[magenta]', 'desc': '[bold][magenta]MAGENTA[/]', 'taken': None},
}

# Start
num_of_players = 4  # int(input('Wieviele Spieler?:\t'))


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


def get_next_player(current: int):  # , max_players: int):
  next_player = current + 1
  if next_player > num_of_players:
    next_player = 1
  return next_player


def new_player(iPlayer: int):
  return False, 0


def get_target_field(pos, iSteps):
  lNext_20_fields = list(dBoard.values())[pos:pos + 20]

  ifields_free = lNext_20_fields[:iSteps].count(field_free)
  ifields_holes = lNext_20_fields[:iSteps].count(field_hole)
  ifields = ifields_free + ifields_holes

  iMoreSteps = iSteps
  while ifields != iSteps:
    iMoreSteps += 1
    ifields_free = lNext_20_fields[:iMoreSteps].count(field_free)
    ifields_holes = lNext_20_fields[:iMoreSteps].count(field_hole)
    ifields = ifields_free + ifields_holes

  iResult = pos + iMoreSteps
  print(f'von Position {pos} {iSteps} Schritte landet auf {iResult}')
  return iResult


def move_player(iPlayer: int, iSteps: int):
  iPos = dPlayers[iPlayer]['positionen'][0]
  iTarget_field = get_target_field(iPos, iSteps)
  if iTarget_field >= num_of_positions:
    dPlayers[iPlayer]['positionen'][0] = num_of_positions
    dBoard[iPos] = field_free
    return True, num_of_positions
  sTarget = dBoard[iTarget_field]

  # Ziel ein Loch
  if sTarget == field_hole:
    dPlayers[iPlayer]['positionen'][0] = 0
    print(f'{field_hole}...')
  # Ziel ist frei
  elif sTarget == field_free:
    dPlayers[iPlayer]['positionen'][0] = iTarget_field
    print(f'{field_free}')

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
      con.print(f'[reverse][red]{field_hole}')
    # with player
    elif field != field_free:
      ifield = int(field)
      scolor = dBoard[ifield]["color"]
      sname = dBoard[ifield]["name"]
      con.print(f'[{scolor}]{sname}[/]')

  con.print()
  con.print('\t'.join(pos[num_of_positions // 3:(num_of_positions // 3) * 2]))
  con.print('\t'.join(loads[num_of_positions // 3:(num_of_positions // 3) * 2]))
  con.print()
  con.print('\t'.join(pos[(num_of_positions // 3) * 2:]))
  con.print('\t'.join(loads[(num_of_positions // 3) * 2:]))
  con.print()


def edit_board():
  for k, v in dPlayers.items():
    print(f"{v['name']}: {v['positionen']}")
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
    'positionen': [0] * 4,
    'color': dColors[iColor]['text']
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
  print("#" * 50)
  print(dPlayers)
  print(dBoard)
  if iCurr_player == 1:
    iRound += 1
    dTimeline[iRound] = []
  if bClearscreen:
    os.system('cls')
  bWin, iTarget_field = False, None
  sCard = None
  sCurr_player = dPlayers[iCurr_player]['name']
  sColor = dPlayers[iCurr_player]['color']
  edit_board()
  show_status_board()
  con.print(f'{sColor}{sCurr_player.upper()}[/], Du bist dran - ziehe eine Karte!')
  input()
  con.print(f"{sColor}{sCurr_player}[/] zieht eine Karte:")
  sCard, lDeck_of_cards = pick_card()
  con.print(f"{sCard = }")

  if sCard == sClick:
    last_hole = hole
    con.print(f'[blue]{sClick}!', end="")
    hole = next(holes)
    # Liste der Löcher aufgebraucht?
    if hole is None:
      # resetten
      holes = click()
      hole = next(holes)
    con.print(f' -> [yellow]-{hole}-')
    if last_hole:
      dBoard[last_hole] = field_free
    dBoard[hole] = field_hole
  else:
    # Player already present on board
    if any(dPlayers[iCurr_player]['positionen']):
      sNew = 'b'  # input('[N]eue Figur oder [B]ewegen?\t')[0].lower()
      if sNew == 'n':
        bWin, iTarget_field = new_player(iCurr_player, sCard)
      else:
        bWin, iTarget_field = move_player(iCurr_player, sCard)
        if bWin:
          con.print(f'YEEAAHH!!!!! {sColor}{sCurr_player}[/] hat gewonnen!!')
    else:
      # Place first player on board
      bWin, iTarget_field = move_player(iCurr_player, sCard)

  turn = [iCurr_player, sCurr_player, sCard, iTarget_field]
  dTimeline[iRound].append(turn)
  if bWin:
    break
  iCurr_player = get_next_player(iCurr_player)  # , num_of_players)

input('Ablauf...')
for round, series in dTimeline.items():
  con.print(f'\n[yellow]######### Runde {round} #########')
  for iplayer, splayer, card, target in series:
    con.print(f'{dPlayers[iplayer]["color"]}{splayer}[/] - {card} -> {target}')

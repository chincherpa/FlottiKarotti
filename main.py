# from time import sleep
import os
import random

from rich.traceback import install
install()

from rich.console import Console
con = Console()

dSpielerNamen = {
  1: 'Flora',
  2: 'Mathea',
  3: 'Lutz',
  4: 'Hannah'
}

bClearscreen = True


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


def get_next_player(current: int, max_players: int):
  next_player = current + 1
  if next_player > max_players:
    next_player = 1
  return next_player


def new_player(iPlayer: int):
  ...


def get_target_field(pos, iSteps):
  # print('get_target_field')
  # print(f'{pos = } - Typ: {type(pos)}')
  # print(f'{iSteps = }')
  lNext_20_fields = list(dBoard.values())[pos:pos + 20]
  # print(f'{lNext_20_fields = }')

  # print(f'{lNext_20_fields[:iSteps] = }')
  ifields_free = lNext_20_fields[:iSteps].count(field_free)
  # print(f'{ifields_free = }')
  ifields_holes = lNext_20_fields[:iSteps].count(field_hole)
  # print(f'{ifields_holes = }')
  ifields = ifields_free + ifields_holes
  # print(f'{ifields = }')

  iMoreSteps = iSteps
  while ifields != iSteps:
    iMoreSteps += 1
    ifields_free = lNext_20_fields[:iMoreSteps].count(field_free)
    ifields_holes = lNext_20_fields[:iMoreSteps].count(field_hole)
    ifields = ifields_free + ifields_holes

  iResult = pos + iMoreSteps
  print(f'von Position {pos} {iSteps} Schritte landet auf {pos + iMoreSteps = }')
  input('weiter...')
  return iResult


def move_player(iPlayer: int, iSteps: int):
  # print('move_player')
  # print(f'{iPlayer = }')
  # print(f'{iSteps = }')
  iPos = dPlayers[iPlayer]['positionen'][0]
  # print(f'{iPos = }')
  iTarget_field = get_target_field(iPos, iSteps)
  # print(f'{iTarget_field = }')
  sTarget = dBoard[iTarget_field]
  # print(f'{sTarget = }')

# Ziel ein Loch
  if sTarget == field_hole:
    dPlayers[iPlayer]['positionen'][0] = 0
    dBoard[iPos] = field_free
    print(f'{field_hole}...')
# Ziel ist frei
  elif sTarget == field_free:
    dPlayers[iPlayer]['positionen'][0] = iTarget_field
    dBoard[iPos] = field_free
    print(f'{field_free}')


def move_player1(iPlayer: int, iSteps: int):
  con.print(f"{dPlayers[iPlayer]['name']} geht {iSteps} vorwärts!")
  last_pos = dPlayers[iPlayer]['positionen'][0]
  iTarget = dPlayers[iPlayer]['positionen'][0] + iSteps
  print(f'Zielposition {iTarget = }')

  if iTarget >= num_of_positions:
    con.print(f"[yellow]YEAH! - {dPlayers[iPlayer]['name']} - HAT GEWONNEN")
    dPlayers[iPlayer]['positionen'][0] = num_of_positions
    dBoard[last_pos] = field_free
    edit_board()
    show_status_board()
    exit()

  # Zielposition ist Loch
  if dBoard[iTarget] == field_hole:
    dPlayers[iPlayer]['positionen'][0] = 0
    dBoard[last_pos] = field_free
    input(f'{field_hole}...')
    return

  # Zielposition schon besetzt
  while True:
    if dBoard[iTarget] != field_free and dBoard[iTarget] != field_hole:
      iTarget += 1
      if iTarget >= num_of_positions:
        con.print(f"[yellow]YEAH! - {dPlayers[iPlayer]['name']} - HAT GEWONNEN")
        dPlayers[iPlayer]['positionen'][0] = num_of_positions
        dBoard[last_pos] = field_free
        edit_board()
        # show_status_board()
        exit()
    else:
      break
  if last_pos:
    dBoard[last_pos] = field_free
  dPlayers[iPlayer]['positionen'][0] = iTarget


def show_status_board():
  pos = [str(x) for x in dBoard.keys()]
  loads = [str(x) for x in dBoard.values()]
  con.print('\t'.join(pos[:num_of_positions // 3]))
  con.print('\t'.join(loads[:num_of_positions // 3]))
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
        dBoard[pos] = v['name'][:7]


field_free = '.'
field_hole = 'Loch'
num_of_ones = 24
num_of_twos = 8
num_of_threes = 4
num_of_clicks = 12
num_of_positions = 28

lones = [1] * num_of_ones
ltwos = [2] * num_of_twos
lthrees = [3] * num_of_threes
lclicks = ['click'] * num_of_clicks
lDeck_of_cards = []

lHoles = [13, 25, 16, 23, 4, 21, 7, 19, 10, None]
dBoard = dict(zip(range(1, num_of_positions + 1), [field_free] * num_of_positions))

dColors = {
  1: {'desc': '[bold][blue]BLAU[/]', 'taken': None},
  2: {'desc': '[bold][red]ROT[/]', 'taken': None},
  3: {'desc': '[bold][green]GRÜN[/]', 'taken': None},
  4: {'desc': '[bold][yellow]GELB[/]', 'taken': None},
  5: {'desc': '[bold][magenta]MAGENTA[/]', 'taken': None},
}

# Start
num_of_players = 4  # int(input('Wieviele Spieler?:\t'))

dPlayers = {}
for i in range(1, num_of_players + 1):
  name = dSpielerNamen[i]  # input(f'Wie heißt Spieler {i}?:\t')
  for k, dic in dColors.items():
    if dic['taken'] is None:
      con.print(f'{k}: {dic["desc"]}')
  iColor = i  #int(input('Welche Farbe?: '))
  dColors[iColor]['taken'] = i
  dPlayers[i] = {
    'name': name,
    'positionen': [0] * 4,
    'color': dColors[iColor]['desc']
  }

for k, v in dPlayers.items():
  con.print(f'Spieler {k}:')
  con.print(f"Name: {v['name']} - {v['positionen']}")


holes = click()
curr_player = 1
hole = None

while True:
  # if bClearscreen:
  #   os.system('clear')
  edit_board()
  show_status_board()
  con.print(f"[yellow]{dPlayers[curr_player]['name']}[/] zieht eine Karte:")
  # sleep(0.1)
  karte, lDeck_of_cards = pick_card()
  con.print(f"{karte = }")

  if karte == 'click':
    last_hole = hole
    con.print('[blue]Click!', end="")
    hole = next(holes)
    if hole is None:
      holes = click()
      hole = next(holes)
    con.print(f' -> [yellow]-{hole}-')
    if last_hole:
      dBoard[last_hole] = field_free
    dBoard[hole] = field_hole
  else:
    # Player already present on board
    if any(dPlayers[curr_player]['positionen']):
      sNew = 'b'  # input('[N]eue Figur oder [B]ewegen?\t')[0].lower()
      if sNew == 'n':
        new_player(curr_player)
      else:
        move_player(curr_player, karte)
    else:
      # Place first player on board
      move_player(curr_player, karte)

  # sleep(1)
  curr_player = get_next_player(curr_player, num_of_players)

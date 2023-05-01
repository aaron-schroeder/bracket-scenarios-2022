import requests
from bs4 import BeautifulSoup

from matchup import MatchupTree


BASE_URL = 'https://fantasy.espn.com/tournament-challenge-bracket/2022/en/entry'
NUM_GAMES_PER_ROUND = [32, 16, 8, 4, 2, 1]


def get_bracket_soup(entry_id):
  page = requests.get(f'{BASE_URL}?entryID={entry_id}')
  return BeautifulSoup(page.content, 'html.parser')


def get_game_tag(soup, round, winner):
  
  assert round < 7

  num_games_before = sum(NUM_GAMES_PER_ROUND[:round-1])
  min_matchup_num = num_games_before + 1
  max_matchup_num = num_games_before + NUM_GAMES_PER_ROUND[round-1]

  def is_right_game(tag):
    # Make sure we are looking at <{tag} class='slots ...'>
    if 'class' not in tag.attrs or 'slots' not in tag['class']:
      return False

    # Make sure the slot is from the right round, based on its parent
    # elem's classname.
    matchup_num = int(tag.parent['class'][1].split('_')[1])
    if (min_matchup_num > matchup_num) or (matchup_num > max_matchup_num):
      return False

    return tag.find(class_='selectedToAdvance').find(class_='name').text == winner

  return soup.find(is_right_game)


def get_winner_tag(game_tag):
  return game_tag.find(class_='selectedToAdvance')


def get_loser_tag(game_tag):
  winner_tag = get_winner_tag(game_tag)
  winner_slot = winner_tag.parent['class'][1]
  # print(winner_slot)
  loser_slot = 's_1' if winner_slot == 's_2' else 's_2' 

  return game_tag.find(class_=loser_slot)


def make_matchup_tree(soup, round=1, winner=None):
  game_tag = get_game_tag(soup, round, winner)

  # winner_tag = get_winner_tag(game_tag)
  loser_tag = get_loser_tag(game_tag)

  if round == 1:
    loser_name = loser_tag.find(class_='name').text
    return MatchupTree(winner, loser_name)
  else:
    # print(game_tag.find_all(class_='picked'))
    # print('')
    # winner_tag = 
    winner_tree = make_matchup_tree(soup, round=round-1, winner=winner)
    loser_name = loser_tag.find(class_='picked').find(class_='name').text
    loser_tree = make_matchup_tree(soup, round=round-1, winner=loser_name)
    # matchups_prev = [
    #   make_matchup_tree(soup, round=round-1, winner=elem.find(class_='name').text)
    #   for elem in game_tag.find_all(class_='picked')
    # ]
    # print(f'R{round}: {[m.winner_name for m in matchups_prev]}')
    # return MatchupTree(matchups_prev[0], matchups_prev[1])
    return MatchupTree(winner_tree, loser_tree)


def make_bracket(entry_id):
  soup = get_bracket_soup(entry_id)
  team_nat_champ = soup.find(class_='champion').find(class_='picked').find(class_='name').text
  
  # Start with the national championship game and recursively build the matchup tree.
  return make_matchup_tree(soup, round=6, winner=team_nat_champ)


if __name__ == '__main__':
  entry_ids = dict(
    aar_1 = 54289747,
    trevor = 59174181,
    kam_2 = 63359730,
    sally = 60632824,
    kam_1 = 63344254,
    sar_1 = 58688111,
    marchywarchy = 63269660,
    sar_2 = 58793709,
    nothingbutnet = 63299095,
    aar_2 = 71791408,
    tess = 59158517,
  )

  # full_bracket = make_bracket(entry_ids['trevor'])

  # import json
  # # print(json.dumps(full_bracket.to_dict(), indent=2))

  # with open('data.json', 'w') as f:
  #   json.dump(full_bracket.to_dict(), f,
  #     indent=2, 
  #     # sort_keys=True
  #   )

  # print(type(matchup_final.winner.winner.winner.winner.winner.winner))
  # print(matchup_final.winner.winner.winner.winner.winner.winner)
  # print(matchup_final.winner.winner.winner.winner.winner.loser)

  # import xml.etree.ElementTree as ET
  # bracket_xml = full_bracket.to_xml()
  # ET.dump(bracket_xml)

  # import xml.etree.ElementTree as ET
  # tree = ET.ElementTree(full_bracket.to_xml())
  # ET.indent(tree, space="\t", level=0)
  # tree.write('trevor.xml')

  # import json
  # with open('sweet_sixteen_test.json', 'w') as f:
  #   json.dump(bracket_xml.to_dict(), f,
  #     indent=2, 
  #     # sort_keys=True
  #   )
  # print(full_bracket.score_by_depth(bracket_xml, 5))

  # See if our brackets pass the shared-reality test.
  # my_soup = get_bracket_soup(me)
  # my_team_nat_champ = my_soup.find(class_='champion').find(class_='picked').find(class_='name').text
  # my_full_bracket = make_matchup_tree(my_soup, round=6, winner=my_team_nat_champ)
  # print(my_full_bracket.is_same_base(full_bracket))  # expect True!

  # for i in range(7):
  #   # l = full_bracket.get_names_by_depth(i)
  #   l = bracket_xml.get_names_by_depth(i)
  #   print(l)

  # debug printing
  # print(matchup_final)  # Don't print, this is HUGE.
  # print(matchup_final.right.right)
  # print(matchup_final.to_dict())

  # import xml.etree.ElementTree as ET
  # tree_file = ET.parse('sweet_sixteen.xml')
  # elem_file = tree_file.getroot()
  # bracket_xml = MatchupTree.from_xml(elem_file)
  # print(full_bracket.score_by_depth(bracket_xml, 0))  # nat champion  
  # print(full_bracket.score_by_depth(bracket_xml, 1))  # nat championship teams
  # print(full_bracket.score_by_depth(bracket_xml, 2))  # final four teams
  # print(full_bracket.score_by_depth(bracket_xml, 3))  # elite 8 teams (has not happened yet)
  # print(full_bracket.score_by_depth(bracket_xml, 4))  # should be 100
  # print(full_bracket.score_by_depth(bracket_xml, 5))  # should be 260
  # print(full_bracket.score_by_depth(bracket_xml, 6))  # unnecessary - just checks teams match.

  import xml.etree.ElementTree as ET

  for name, entry_id in entry_ids.items():
    guesses = make_bracket(entry_id)
    tree = ET.ElementTree(guesses.to_xml())
    ET.indent(tree, space="\t", level=0)
    tree.write(f'data/{name}.xml')
  
    # ALL good through the sweet 16!
    # print(
    #   f'{name}\n'
    #   f'{"-" * len(name)}\n'
    #   f'Round 1: {guesses.score_by_depth(bracket_xml, 5)}\n'
    #   f'Round 2: {guesses.score_by_depth(bracket_xml, 4)}\n'
    #   # f'{entry}'
    # )

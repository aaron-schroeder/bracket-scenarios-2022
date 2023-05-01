"""scenarios.py"""
import xml.etree.ElementTree as ET

from matchup import MatchupTree as MT


def read_xml_file(path):
  tree_file = ET.parse(path)
  elem_file = tree_file.getroot()
  return MT.from_xml(elem_file)
  

# --------------------------------------------------------------------
# Consider all possible remaining scenarios from this point,
# and calculate scores accordingly.

# Load a bracket with the correct sweet 16 teams with an arbitrary
# path to the NC (Gonzaga over Arizona)
sweet_sixteen = read_xml_file('data/sweet_sixteen.xml')

def generate_paths(depth=3):
  """This is gross and could be made more elegant"""

  # 1, 3, 7, 15, 31, 63
  num_trees = 2 ** (depth + 1) - 1
  
  # Build a complete set of scenario paths
  paths = ['']
  # trees = [hypo_bracket]
  # scores = []
  for _ in range(num_trees):
    expanded_paths = [path + str(0) for path in paths] + [path + str(1) for path in paths]
    paths = expanded_paths
  
  return paths

# I want to make a recursive function but I cannot imagine what it looks like yet.
# def test_scenarios(hypo_bracket, hypo_sub_bracket, guess_bracket, depth, score_dict):
def test_scenarios(hypo_bracket, guess_bracket, depth=3):

  trees = hypo_bracket.get_every_tree(depth)

  # Consider the switched and unswitched cases for each tree,
  # in every configuration.
  
  # Build a complete set of scenario paths
  paths = generate_paths(depth)

  # print(paths)
  # print(len(paths))  # 2, 8, 128, 32768

  # score each scenario
  scores = dict()
  for path in paths:
    # switch/don't switch the winner of the tree at each position
    for i, is_switched in enumerate(path):
      if bool(int(is_switched)):
        trees[i].switch_winner()

    # score the bracket corresponding to this path
    scores[path] = guess_bracket.score(hypo_bracket)

    # switch back
    for i, is_switched in enumerate(path):
      if bool(int(is_switched)):
        trees[i].switch_winner()
    
  return scores


# Load a bracket that is affected by these two teams in the NC.
# (Sally has Arizona over Gonzaga)
# bracket = read_xml_file('data/sally.xml')
# bracket = read_xml_file('data/aar_1.xml')

# Test switching the national champion back and forth
# print(f'National champion = {sweet_sixteen.winner_name} ({bracket.score(sweet_sixteen)})')
# sweet_sixteen.switch_winner()
# print(f'National champion = {sweet_sixteen.winner_name} ({bracket.score(sweet_sixteen)})')
# Expected to add 320 to the total score when I switch the scenario to an Arizona NC,
# and I was right! (840 -> 1160)

# scores = test_scenarios(sweet_sixteen, bracket)
# print(scores)

def max_points(fname):
  bracket = read_xml_file(fname)
  scores = test_scenarios(sweet_sixteen, bracket)
  print(f'{fname}: {max(scores.values())}')

# max_points('data/kam_1.xml')
# max_points('data/kam_1.xml')

# Test all brackets.
# import glob
# for fname in glob.glob('data/*.xml'):
#   max_points(fname)

# ---------------------------------------------------------------------

def print_winners(trees, path):
  big_daddy = trees[0]
  for i, bin_string in enumerate(path):
    is_switched = bool(int(bin_string))
    if is_switched:
      trees[i].switch_winner()
  for tree in trees:
    print(f'{tree.winner_name} over {tree.loser_name}')


def generate_dataframe(hypo_bracket):
  """Build a DataFrame of scenarios"""
  trees = hypo_bracket.get_every_tree(depth=3)

  # Build a complete set of scenario paths
  paths = generate_paths(depth=3)

  # Load every bracket
  # eg brackets['sar_1'] = MatchupTree('Gonzaga')
  import glob
  brackets = {fname.split('/')[1].split('.')[0]: read_xml_file(fname) for fname in glob.glob('data/*.xml')}

  # score each scenario
  scores = []
  for path in paths:
    # switch/don't switch the winner of the tree at each position
    for i, is_switched in enumerate(path):
      if bool(int(is_switched)):
        trees[i].switch_winner()

    # score the bracket corresponding to this path
    # scores[path] = bracket.score(sweet_sixteen)
    scores.append({name: bracket.score(hypo_bracket) for name, bracket in brackets.items()})

    # switch back
    for i, is_switched in enumerate(path):
      if bool(int(is_switched)):
        trees[i].switch_winner()

  import pandas as pd
  df = pd.DataFrame(scores, index=paths)
  return df

# Each of these represents the exact path of one of the S16 teams.
# paths_to_s16 = [
#   sweet_sixteen.winner.winner.winner.winner,
#   sweet_sixteen.winner.winner.winner.loser,
#   sweet_sixteen.winner.winner.loser.winner,
#   sweet_sixteen.winner.winner.loser.loser,
#   sweet_sixteen.winner.loser.winner.winner,
#   sweet_sixteen.winner.loser.winner.loser,
#   sweet_sixteen.winner.loser.loser.winner,
#   sweet_sixteen.winner.loser.loser.loser,
#   sweet_sixteen.loser.winner.winner.winner,
#   sweet_sixteen.loser.winner.winner.loser,
#   sweet_sixteen.loser.winner.loser.winner,
#   sweet_sixteen.loser.winner.loser.loser,
#   sweet_sixteen.loser.loser.winner.winner,
#   sweet_sixteen.loser.loser.winner.loser,
#   sweet_sixteen.loser.loser.loser.winner,
#   sweet_sixteen.loser.loser.loser.loser,
# ]

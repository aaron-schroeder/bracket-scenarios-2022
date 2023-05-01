import xml.etree.ElementTree as ET

import util


class MatchupTree:
  def __init__(self, winner, loser):
    """Initialize MatchupTree with a winner and loser object.
    
    winner, loser (MatchupTree or str): object representing the competitors
     in an individual matchup.
    """
    classtype = type(self)
  
    if not isinstance(winner, (str, classtype)):
      raise TypeError(f'`winner` arg must be str or {classtype.__name__}')

    if not isinstance(loser, (str, classtype)):
      raise TypeError(f'`loser` arg must be str or {classtype.__name__}')

    self.winner = winner
    self.loser = loser

  @property
  def winner_name(self):
    if isinstance(self.winner, str):
      return self.winner
    else:
      return self.winner.winner_name

  @property
  def loser_name(self):
    if isinstance(self.loser, str):
      return self.loser
    else:
      return self.loser.winner_name

  @property
  def depth(self):
    """HACK: Assumes no weird play-in games.
    
    depth = 0 means this tree is just a game.
    """
    max_depth = 0
    elem = self
    while isinstance(elem.winner, MatchupTree):
      max_depth += 1
      elem = elem.winner

    return max_depth

  def score(self, actual):
    """Score this MatchupTree against another representing the actual results."""   
    return sum([self.score_by_depth(actual, i) for i in range(self.depth + 1)])

  def score_by_depth(self, actual, depth):
    points_per_round = 320  # accept as input

    # if not self.is_same_base(actual):
    #   raise ValueError('Cannot compare two brackets representing different configurations.')

    teams1 = self.get_names_by_depth(depth)
    teams2 = actual.get_names_by_depth(depth)

    points_per_game = points_per_round / len(teams1)

    return points_per_game * sum([team in teams2 for team in teams1])

  def is_same_base(self, other):
    """Check if this bracket represents the same set of competitors as another"""
    root1 = util.get_sorted_clean_elem(self.to_xml())
    root2 = util.get_sorted_clean_elem(other.to_xml())
        
    return ET.tostring(root1) == ET.tostring(root2)

  def get_names_by_depth(self, depth):
    """Return a list of competitors based on depth in the bracket.

      depth = 0: national champion
      depth = 1: national championship teams
      depth = 2: final four teams
      depth = 3: elite 8 teams
      depth = 4: sweet 16 teams
      depth = 5: round of 32 teams
      depth = 6: round of 64 teams
      depth = 7: (WIP) play-in games (first four teams)      
    """
    if depth == 0:  # Kind of hacky, returns a different type, maybe unnecessary
      return [self.winner_name]
    elif depth == 1:
      return [self.winner_name, self.loser_name]
    else:
      list_left = self.winner.get_names_by_depth(depth - 1)
      list_right = self.loser.get_names_by_depth(depth - 1)
      return list_left + list_right
  
  @classmethod
  def from_dict(cls, d):
    if isinstance(d['winner'], str):
      winner = d['winner']
    elif isinstance(d['winner'], dict):
      winner = cls.from_dict(d['winner'])
    else:
      raise TypeError

    if isinstance(d['loser'], str):
      loser = d['loser']
    elif isinstance(d['loser'], dict):
      loser = cls.from_dict(d['loser'])
    else:
      raise TypeError

    return cls(winner, loser)

  @classmethod
  def from_xml(cls, x):
    """Expects ET.Element"""
    assert len(x) == 2

    for child in x:
      if child.get('winner') == 'true':
        elem_win = child
      else:
        elem_lose = child

    if elem_win.text is not None and elem_win.text.strip() != '':
      winner = elem_win.text
    else:
      winner = cls.from_xml(elem_win)

    if elem_lose.text is not None and elem_lose.text.strip() != '':
      loser = elem_lose.text
    else:
      loser = cls.from_xml(elem_lose)

    return cls(winner, loser)

  def to_dict(self):
    if isinstance(self.winner, str):
      winner = self.winner
    else:
      winner = self.winner.to_dict()

    if isinstance(self.loser, str):
      loser = self.loser
    else:
      loser = self.loser.to_dict()   

    return {
      'winner': winner,
      'loser': loser
    }

  def to_list(self):
    if isinstance(self.winner, str):
      winner = self.winner
    else:
      winner = self.winner.to_list()

    if isinstance(self.loser, str):
      loser = self.loser
    else:
      loser = self.loser.to_list()

    return [winner, loser]

  def to_xml(self, level=0):
    """Returns a <BracketTree> element if level == 0,
       otherwise a 2-element list to fit inside a parent element.
       
    """
    tag_name = f'depth_{level}'
    # tag_name = f'round_of_{2 ** (level + 1)}'  # eg round of 2, 4, 8, 16, ...

    elem_win = ET.Element(
      tag_name, 
      attrib={'winner': "true"}
    )
    elem_lose = ET.Element(
      tag_name, 
      # attrib={'winner': False}
    )

    if isinstance(self.winner, str):
      elem_win.text = self.winner
    else:
      elem_win.extend(self.winner.to_xml(level + 1))

    if isinstance(self.loser, str):
      elem_lose.text = self.loser
    else:
      elem_lose.extend(self.loser.to_xml(level + 1))

    if level == 0:
      root = ET.Element('BracketTree')
      root.extend([elem_win, elem_lose])
      return root
    else:
      return [elem_win, elem_lose]

  def switch_winner(self):
    """Switch the winner and loser of the game this tree represents."""
    new_winner = self.loser
    new_loser = self.winner
    self.winner = new_winner
    self.loser = new_loser

  def get_trees_by_depth(self, depth):
    curr_depth = 0
    trees = [self]
    while curr_depth < depth:
      trees_nested = [[tree.winner, tree.loser] for tree in trees]
      
      # flat_list = [item for sublist in regular_list for item in sublist]
      trees = [team for tree in trees_nested for team in tree]

      curr_depth += 1

    return trees

  def get_every_tree(self, depth):
    curr_depth = 0
    trees_this_level = [self]
    trees = [self]
    while curr_depth < depth:
      trees_next_level_nested = [[tree.winner, tree.loser] for tree in trees_this_level]
      
      # trees_nested = [[tree.winner, tree.loser] for tree in trees]
      # # flat_list = [item for sublist in regular_list for item in sublist]
      # trees.extend([team for tree in trees_nested for team in tree])

      # Send things to the next loop
      # example: flat_list = [item for sublist in regular_list for item in sublist]
      trees_this_level = [team for tree in trees_next_level_nested for team in tree]
      trees.extend(trees_this_level)
      curr_depth += 1

    return trees

  def __repr__(self):
    return f'MatchupTree({self.winner_name}, depth={self.depth})'

  def __str__(self):
    """WORK IN PROGRESS"""
    # lines = self._build_tree_string(0)[0]
    # return "\n" + "\n".join((line.rstrip() for line in lines))

    root = self.to_xml()
    ET.indent(root, space="\t", level=0)

    return ET.tostring(root, encoding='unicode')

  def _build_tree_string(self, curr_index):
    """WORK IN PROGRESS - would rather make a vertical than horizontal bracket"""
    
    # if isinstance(self.winner, str) and isinstance(self.loser, str):
    #   return [], 0, 0, 0

    line1 = []
    line2 = []

    node_repr = self.winner_name

    new_root_width = gap_size = len(node_repr)

    if isinstance(self.winner, str) and isinstance(self.loser, str):
      # if self.left is None and self.right is None:
      l_box, l_box_width, l_root_start, l_root_end = [], 0, 0, 0
      r_box, r_box_width, r_root_start, r_root_end = [], 0, 0, 0
    else:

      # Get the left and right sub-boxes, their widths, and root repr positions
      l_box, l_box_width, l_root_start, l_root_end = self.winner._build_tree_string(
        2 * curr_index + 1
      )
      r_box, r_box_width, r_root_start, r_root_end = self.loser._build_tree_string(
        2 * curr_index + 2
      )

    # Draw the branch connecting the current root node to the left sub-box
    # Pad the line with whitespaces where necessary
    if l_box_width > 0:
      l_root = (l_root_start + l_root_end) // 2 + 1
      line1.append(" " * (l_root + 1))
      line1.append("_" * (l_box_width - l_root))
      line2.append(" " * l_root + "/")
      line2.append(" " * (l_box_width - l_root))
      new_root_start = l_box_width + 1
      gap_size += 1
    else:
      new_root_start = 0

    # Draw the representation of the current root node
    line1.append(node_repr)
    line2.append(" " * new_root_width)

    # Draw the branch connecting the current root node to the right sub-box
    # Pad the line with whitespaces where necessary
    if r_box_width > 0:
      r_root = (r_root_start + r_root_end) // 2
      line1.append("_" * r_root)
      line1.append(" " * (r_box_width - r_root + 1))
      line2.append(" " * r_root + "\\")
      line2.append(" " * (r_box_width - r_root))
      gap_size += 1
    new_root_end = new_root_start + new_root_width - 1

    # Combine the left and right sub-boxes with the branches drawn above
    gap = " " * gap_size
    new_box = ["".join(line1), "".join(line2)]
    for i in range(max(len(l_box), len(r_box))):
      l_line = l_box[i] if i < len(l_box) else " " * l_box_width
      r_line = r_box[i] if i < len(r_box) else " " * r_box_width
      new_box.append(l_line + gap + r_line)

    # Return the new box, its width and its root repr positions
    return new_box, len(new_box[0]), new_root_start, new_root_end


class MatchupTreeOld:
  def __init__(self, winner, left=None, right=None):
    self.winner = winner
    self.left = left
    self.right = right

  def to_json(self):
    if self.left is None and self.right is None:
      return self.winner
    return {'winner': {self.left.to_json(), self.right.to_json()}}

  def from_json(self):
    pass

  def __str__(self):
    lines = self._build_tree_string(0)[0]
    return "\n" + "\n".join((line.rstrip() for line in lines))

  def _build_tree_string(self, curr_index):
    line1 = []
    line2 = []

    node_repr = str(self.winner)

    new_root_width = gap_size = len(node_repr)

    if self.left is None and self.right is None:
      l_box, l_box_width, l_root_start, l_root_end = [], 0, 0, 0
      r_box, r_box_width, r_root_start, r_root_end = [], 0, 0, 0
    else:
      # Get the left and right sub-boxes, their widths, and root repr positions
      l_box, l_box_width, l_root_start, l_root_end = self.left._build_tree_string(
        2 * curr_index + 1
      )
      r_box, r_box_width, r_root_start, r_root_end = self.right._build_tree_string(
        2 * curr_index + 2
      )

    # Draw the branch connecting the current root node to the left sub-box
    # Pad the line with whitespaces where necessary
    if l_box_width > 0:
      l_root = (l_root_start + l_root_end) // 2 + 1
      line1.append(" " * (l_root + 1))
      line1.append("_" * (l_box_width - l_root))
      line2.append(" " * l_root + "/")
      line2.append(" " * (l_box_width - l_root))
      new_root_start = l_box_width + 1
      gap_size += 1
    else:
      new_root_start = 0

    # Draw the representation of the current root node
    line1.append(node_repr)
    line2.append(" " * new_root_width)

    # Draw the branch connecting the current root node to the right sub-box
    # Pad the line with whitespaces where necessary
    if r_box_width > 0:
      r_root = (r_root_start + r_root_end) // 2
      line1.append("_" * r_root)
      line1.append(" " * (r_box_width - r_root + 1))
      line2.append(" " * r_root + "\\")
      line2.append(" " * (r_box_width - r_root))
      gap_size += 1
    new_root_end = new_root_start + new_root_width - 1

    # Combine the left and right sub-boxes with the branches drawn above
    gap = " " * gap_size
    new_box = ["".join(line1), "".join(line2)]
    for i in range(max(len(l_box), len(r_box))):
      l_line = l_box[i] if i < len(l_box) else " " * l_box_width
      r_line = r_box[i] if i < len(r_box) else " " * r_box_width
      new_box.append(l_line + gap + r_line)

    # Return the new box, its width and its root repr positions
    return new_box, len(new_box[0]), new_root_start, new_root_end


if __name__ == '__main__':  # debug time
  m = MatchupTree(
    MatchupTree('a', 'c'), 
    MatchupTree('b', 'd')
  )
  mrev = MatchupTree(
    MatchupTree('d','b'), 
    MatchupTree('c', 'a')
  )
  mdiff = MatchupTree(
    MatchupTree('a','b'), 
    MatchupTree('c', 'd')
  )
  mact = MatchupTree(
    MatchupTree('b','d'), 
    MatchupTree('c', 'a')
  )
  m_ee = MatchupTree(
    MatchupTree(
      MatchupTree('a', 'c'), 
      MatchupTree('b', 'd')
    ),
    MatchupTree(
      MatchupTree('e', 'f'), 
      MatchupTree('g', 'h')
    ),
  )

  # debug
  # print(m_ee.get_every_tree(0))
  # print(m_ee.get_every_tree(1))
  # print(m_ee.get_every_tree(2))
  # print(m_ee.get_every_tree(3))
  print(len(m_ee.get_every_tree(0)))  # expect 1
  print(len(m_ee.get_every_tree(1)))  # expect 3
  print(len(m_ee.get_every_tree(2)))  # expect 7
  print(len(m_ee.get_every_tree(3)))  # expect 15

  # debug
  # print(m_ee.get_trees_by_depth(0))
  # print(m_ee.get_trees_by_depth(1))
  # print(m_ee.get_trees_by_depth(2))
  # print(m_ee.get_trees_by_depth(3))

  # debug switch_winner()
  # print(m)  # waiting on a nice print function...
  # # print(f'Initial winner:\n{m.winner} ({m.winner_name})\n')
  # # print(f'Initial loser:\n{m.loser} ({m.loser_name})\n')
  # m.switch_winner()
  # print(m)  # waiting on a nice print function...
  # # print(f'Switched winner:\n{m.winner} ({m.winner_name})\n')
  # # print(f'Switched loser:\n{m.loser} ({m.loser_name})\n')

  # debug base check
  # print(m.is_same_base(mrev))  # expect True
  # print(m.is_same_base(mdiff))  # expect False

  # debug scoring by round
  # print(m.score_by_depth(mrev, 0))  # expect 0
  # print(m.score_by_depth(mrev, 1))  # expect 0
  # print(m.score_by_depth(mact, 0))  # expect 0
  # print(m.score_by_depth(mact, 1))  # expect 320
  # # The following give reasonable results, but not ideal behavior
  # print(m.score_by_depth(mact, 2))  # expect 640, because no games have been played
  # print(m.score_by_depth(mact, 3))  # throws an ugly error

  # debug scoring
  # print(m.score(mrev))  # expect 0
  # print(m.score(mact))  # expect 320
  # print(m.score(m))  # expect 640 * 2 = 1280

  # debug xml roundtrip
  # elem = m.to_xml()
  # ET.dump(elem)
  # m_xml = MatchupTree.from_xml(elem)
  # print(m_xml.winner_name)
  # elem_xml = m_xml.to_xml()
  # ET.dump(elem_xml)

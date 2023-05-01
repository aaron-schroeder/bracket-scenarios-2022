import xml.etree.ElementTree as ET


def get_first_child_text(elem):
  val = elem.text
  while val is None:
    sortlist = sorted([get_first_child_text(child) for child in elem])
    val = sortlist[0]
  return val


def get_sorted_clean_elem(elem):
  import copy
  out = copy.deepcopy(elem)
  out[:] = sorted(elem, key=lambda child: get_first_child_text(child))
  for child in out:
    child.attrib.pop('winner', None)
    child[:] = get_sorted_clean_elem(child)

  return out

if __name__ == '__main__':  # test things out

  e = ET.Element('BracktTree')
  w = ET.SubElement(e, 'level_0')
  l = ET.SubElement(e, 'level_0')
  ww = ET.SubElement(w, 'level_1')
  wl = ET.SubElement(w, 'level_1')
  lw = ET.SubElement(l, 'level_1')
  ll = ET.SubElement(l, 'level_1')

  # ww.text = 'A'  # Expected element order after sorting
  # wl.text = 'C'
  # lw.text = 'B'
  # ll.text = 'D'

  # ww.text = 'D'
  # wl.text = 'B'
  # lw.text = 'C'
  # ll.text = 'A'

  # One play-in game
  ww.text = 'D'
  wl.text = 'B'
  lw.text = 'C'
  llw = ET.SubElement(ll, 'level_2')
  lll = ET.SubElement(ll, 'level_2')
  llw.text = 'E'
  lll.text = 'A'

  ET.dump(e)
  # sort_func(e)  # does not change the input, as it stands.
  # ET.dump(e)
  e_new = get_sorted_clean_elem(e)
  ET.dump(e_new)
  ET.dump(e)

  # print(get_first_child_text(e))   # should be 'A'
  # print(get_first_child_text(w))   # should be 'B'
  # print(get_first_child_text(l))   # should be 'A'
  # print(get_first_child_text(ww))  # should be 'D'
  # print(get_first_child_text(ll))  # should be 'A'


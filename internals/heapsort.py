# there is a heapq package for heap sort, but what I need is
# on receiving response remove particular RunningRequest
# from heapified array.
# for this purpose I head the RunningRequest structure to track
# its own position.

import typing

class HeapsortArray:
  def __init__(self, arr: typing.List, less_than_comparator: typing.Callable[[typing.Any, typing.Any], bool], on_index_change_callback: typing.Callable[[int], None] = None):
    self.array = arr
    self._lt_comparator = less_than_comparator
    self._on_index_change_callback = on_index_change_callback
    self.heapify()
  
  def __getitem__(self, key):
    return self.array[key]

  def __len__(self):
    return len(self.array)
  
  def heapify(self):
    for i in range(len(self.array)//2-1, -1, -1):
      self._sink(i)

  def push(self, element):
    i = len(self.array)
    self.array.append(element)
    if self._on_index_change_callback is not None:
      self._on_index_change_callback(element, i)
    self._arise(i)

  def _arise(self, i):
    while True:
      next_i = self._arise_local(i)
      if next_i == i:
        break
      i = next_i
  
  def remove_element(self, i):
    if i == len(self.array)-1:
      self.array.pop()
    else:
      self._swap(i, len(self.array)-1)
      self.array.pop()
      self._sink(i)
      self._arise(i)

  def pop(self):
    top_element = self.array[0]
    self.remove_element(0)
    return top_element

  def _left_child_idx(self, i: int) -> int:
    return i*2+1

  def _right_child_idx(self, i: int) -> int:
    return i*2+2

  def _parent_idx(self, i: int) -> int:
    return (i-1)//2
  
  def _swap(self, i: int, j: int):
    self.array[i], self.array[j] = self.array[j], self.array[i]
    if self._on_index_change_callback is not None:
      self._on_index_change_callback(self.array[i], i)
      self._on_index_change_callback(self.array[j], j)

  def _sink_local(self, i: int) -> int:
    left_idx = self._left_child_idx(i)
    right_idx = self._right_child_idx(i)

    if left_idx >= len(self.array):
      return i
    left = self.array[left_idx]

    smallest_parent_idx = left_idx
    if right_idx < len(self.array):
      right = self.array[right_idx]
      if self._lt_comparator(right, left):
        smallest_parent_idx = right_idx

    smallest_parent = self.array[smallest_parent_idx]
    if self._lt_comparator(smallest_parent, self.array[i]):
      self._swap(i, smallest_parent_idx)
      return smallest_parent_idx
    return i
  
  def _sink(self, i: int) -> int:
    while True:
      next_i = self._sink_local(i)
      if next_i == i:
        break
      i = next_i
  
  def _arise_local(self, i: int) -> int:
    if i == 0:
      return 0
    parent_idx = self._parent_idx(i)
    current = self.array[i]
    parent =  self.array[parent_idx]
    if self._lt_comparator(current, parent):
      self._swap(i, parent_idx)
      return parent_idx
    return i

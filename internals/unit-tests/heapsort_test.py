# there is a heapq package for heap sort, but what I need is
# on receiving response remove particular RunningRequest
# from heapified array.
# for this purpose I head the RunningRequest structure to track
# its own position.

import heapsort
import random

def check_invariant(heap_arr: heapsort.HeapsortArray):
  for i in range(len(heap_arr.array)//2-1):
    assert heap_arr._lt_comparator(heap_arr.array[i], heap_arr.array[heap_arr._left_child_idx(i)]), f"in array element with index {i} ({heap_arr.array[i]}) is in wrong position" 
    assert heap_arr._lt_comparator(heap_arr.array[i], heap_arr.array[heap_arr._right_child_idx(i)]), f"in array element with index {i} ({heap_arr.array[i]}) is in wrong position" 

def test_heapify_small_array():
  arr = [3, 2, 1]
  heap_arr = heapsort.HeapsortArray(arr, lambda x, y: x < y, None)
  assert heap_arr.array[0] < heap_arr.array[1], heap_arr.array # check_invariant(heap_arr)
  assert heap_arr.array[0] < heap_arr.array[2], heap_arr.array

def test_heapify():
  arr = random.sample(range(-1, 50), 30)
  heap_arr = heapsort.HeapsortArray(arr, lambda x, y: x < y, None)
  check_invariant(heap_arr)

def test_push():
  arr = random.sample(range(-1, 50), 30)
  heap_arr = heapsort.HeapsortArray([], lambda x, y: x < y, None)
  for el in arr:
    heap_arr.push(el)
    check_invariant(heap_arr)

def test_remove_element_small_array():
  length = 5
  arr = random.sample(range(-1, 50), length)
  heap_arr = heapsort.HeapsortArray(arr, lambda x, y: x < y, None)
  for i in range(length):
    heap_arr.remove_element(random.randint(0, length-i-1))
    check_invariant(heap_arr)

def test_remove_element():
  length = 30
  arr = random.sample(range(-1, 50), length)
  heap_arr = heapsort.HeapsortArray(arr, lambda x, y: x < y, None)
  for i in range(length):
    heap_arr.remove_element(random.randint(0, length-i-1))
    check_invariant(heap_arr)
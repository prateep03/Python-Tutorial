# a = [1, 2, 3, 'tutorial'] # mutable
# print(a)
#

# a = [1, 2, 3.142, 'python','anaconda','spyder']
# print(type(a))
# print(a[0],a[1],a[2])
#
# # a[0] = 'rabbit'
# # print(a)
#
# a.append(1.414)
# print(a)
#
# a.insert(1, -2)
# print(a)
#
# b = a.pop(0)
# print("Pop = ", a, b)
#
# print(len(a))
# print(repr(a), type(repr(a)))
#
# b = [2, 3, 1]
# # b.sort(reverse=True)
# # b = sorted(b, reverse=False)
# b.reverse()
# print("B = ", b)

# c = b.copy() # deep-copy
#
# print("id(b) = ", id(b))
# print("id(c) = ", id(c))
#
# c[0] = 4
# print("b = ",b)
# print("c = ", c)
#
# empty = []
# l = [empty] * 5
# print(l)

# l[1].append('python1')
# l[1] = ['python1']
# l[0].append('python2')
# print(l)
# print([id(ll) for ll in l])
#
# a = [0,1,2,3]
# am = [i for i in range(4)]
# print(a, am)

# # Immutable and mutable
# # block comment - Ctrl + /
# # uncomment block - Ctrl + /
# # a[0] = 2
# # print(a)
#
# a.append(4)
# print(a)
#
# a.append(3)
# print(a)
#
# # a.remove(3)
# print(a)
#
# # print(a.count(3))
#
# # b = a
# # b.reverse()
# # print(b)
# # print(a)
#
# a.pop(3)
# print(a)
#
# print(a.index(3))
#
# a.sort(reverse=True)
# print(a)

## Tuples
b = ('apple','orange')
print(b)
# print(type(b))

# b[0] = 'kiwi'
# print(b[0])

# if, else, elif
# if condition is True:
#    do this
# else:
#    do that
# if 'apple' not in b:
#     print('apple is there')
# else:
#     print('no')

print(len(b))
bb = list(b)
bb.append('kiwi')
bb = tuple(bb)
print(bb)

## Set
# c = {1, 2, 3, 'apple'}
# cc = {1, 2, 3}
# print(c)
#
# # print(c[0]) # wrong
#
# c.add('orange')
# print(c)
#
# c.update(['kiwi','banana'])
# print(c)
#
# # c.remove('kiwii')
# # print(c)
#
# print(c.difference(cc))

## Dictionary - key-value pair
# d = {'a': 1, 'b': 2}
# print(len(d))
#
# for k in d.iteritems():
#     print(k)
#
# print(d['a'])
#
# # d['a'] = 3
# d['c'] = 4
# print(d)
#
# print('a' in d)
#
# if 'c' in d:
#     print(d['c'])
# else:
#     print('c doesn''t exist in d')
#
# d.pop('b')
# print(d)
#
# print(type(d.values()))
#
# dd = list(d)
# print(dd)

## If-else
# # ==, !=, >, >=, <, <= --> comparison operators
# # ||(or), &&(and)--> comparison operators
# # |, & --> bitwise operator
#
# # (x and y) is true iff x is true and y is true
# # (x or y) is true if x is true or y is true
# a = 3
# b = 4
# c = 2
# # A
# if a > b:
#     print("a is greater than b")
# elif a == b:
#     print("a is equal to b")
# elif a < b:
#     print("a is less than b")
#
# # B
# if a > b:
#     print("a is greater than b")
# else:
#     if a == b:
#         print("a is equal to b")
#     else:
#         if a < b:
#             print("a is less than b")
#
# #
# # if a == 3:
# #     print(a)
# # else:
# #     print(b)
#
# # a = 3 # 1 + 2^1 * 1 + 2^2 * 0 = 011
# # 4 # 0 + 2^1 * 0 + 2^2 * 1     = 100
# # # 7 = 1 + 2^1 * 1 + 2^2 * 1   = 111
#
# print("a is greater than b") if a > b else print("a is equal to b") if a == b else print("a is less than b") if a < b else print("")

## Loops
#  for, while

# *
# **
# ***
# ****
# *****

#   *   --> 1
#  ***  --> 3
# ****** --> 5

# Add integers from 1 to 10
# result = 1
# for a in range(1,10):
#     # print(a)
#     result = result * a
#
# result1 = 1
# for a in range(1,10):
#     # print(a)
#     for b in range(1,a):
#         result1 = result1 * b
#
# print("multiply {}".format(result))

# a = 1
# result2 = 0
# while a < 10:
#     result2 = result2 + a
#     a = a + 1
#
# print("result2 {}".format(result2))
#
# mutable - you can change elements of the object
# immutable - you cannot change elements of the object

# a = [1,2,3] # mutable
# a[0] = 4
# print(a)
#
# b = 'python' # immutable
# # substring : continuous sequence of characters
# # subsequence : not necessarily continuous ('pto') -> [0, 2, 5]
# # b[0] = 'c'
# # print(b)
# id = b.find('ht')
# print(id)


# thistuple = ("apple", "banana", "cherry")

# thislist = [x + x for x in thistuple]
# # for x in thistuple:
# #     thislist.append(x)
#
# print(thislist)

thistuple = tuple("apple")
# print(type(thistuple), thistuple)

thisset = {3,2,1}
thislist = list(thisset)

thislist.sort()
# print(thislist)

# b.strip()
# print('{0} {1:0.3f}'.format(1,22/7))
#
# print('%d' % (2 > 1), end=' ')
# print('2')

'''
Logical operator
  - and : return x if x is False otherwise return y
  - or : return y if x is False otherwise return x
  - not : return True is x is False, else False
'''

# class MyNum:
#     def __iter__(self):
#         self.a = 1
#         return self
#
#     def __next__(self):
#         x = self.a
#         self.a += 1
#         return x
#
# mm = MyNum()
# iter = 0
# for i in mm:
#     if iter >= 5:
#         break
#     print(i)
#     iter += 1

# a = 'Eadureka'
# print(a.count('a',2,len(a)))
# print(a.find('rrek'))
#
# tup = ('a','b')
# print(tup + ('c',''))
# print(tup)
#
# a = {1:'a',2:'b'}
# a.update({3:'c'})
# print(a)
#
# for i in range(9,0,-1):
#     print(i,end=' ')
#
# def fibo(n):
#     a = 0
#     b = 1
#     for x in range(n):
#         c = a + b
#         a = b
#         b = c
#         print(a,' ')
#     return b
#
# n = int(input())
# fibo(n)


# from memory_profiler import profile
#
# @profile(precision=4)
# def my_func():
#     a = [1] * (10 ** 6)
#     b = [2] * (2 * 10 ** 7)
#     del b
#     return a
#
# if __name__ == "__main__":
#     my_func()


# query = """
# select * from a where
# adasdfsfds
# """
#
# print(query)

def myfunc(x):
    return x+1

def myfunc1(x=3):
    return x+1

def myfunc2(*args, **kwargs):
    pass

myfunc2(1,2,34,34343,43343,name="python")



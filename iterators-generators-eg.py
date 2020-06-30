nums = [1,2,3]

i_nums =  iter(nums)
i2_nums = nums.__iter__()

# print(str(i_nums))
# print(str(i2_nums))


# Iterable : object over which you can iterate
# Iterator : an iterator object. MUST have a '__next__' method
# for num in nums:
#     print(num)

# call next() for every element in tuple
mytuple = ("apple", "banana", "cherry")
mylst = [x for x in mytuple]
# myit = iter(mytuple)
#
# print(next(myit))
# print(next(myit))
# print(next(myit))
# print(next(myit))


# mystr = "banana"
# myit = iter(mystr)
#
# while True:
#     try:
#         print(next(myit))
#     except StopIteration:
#         break


# i_nums = iter(nums) # i_nums is an iterator object, having __next__ method

# print(dir(i_nums))
# print(next(i_nums))
# print(next(i_nums))
# print(next(i_nums))

class Range(object):

    def __init__(self, start, end, step = 1):
        self.value = start
        self.end = end
        self.step = step

    def __iter__(self):
        return self

    def __next__(self):
        if self.value >= self.end:
            raise StopIteration
        current = self.value
        self.value += self.step
        return current # generator

r = Range(1,10,4) # [1,2,3,4,5,6,7,8,9,10]
# i_r = iter(r)
# print(next(i_r))
# print(next(i_r))
# print(next(i_r))
# print(next(i_r))

# for i in r:
#     print(i)

'''
# for i in r:
#     print(i)

'''
def square(num):
    for i in range(num):
        yield i*i

gen = square(3)
print(type(gen))
for i in gen:
    print(i)


# import random
#
# def lottery():
#     # returns 6 numbers between 1 and 40
#     for i in range(6):
#         yield i, random.randint(1, 40)
#
#     # returns a 7th number between 1 and 15
#     yield 6, random.randint(1,15)
#
# for idx, random_number in lottery():
#        print("Iter: %d, the next number is... %d!" %(idx, random_number))
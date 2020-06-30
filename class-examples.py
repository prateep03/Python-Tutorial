import math
from datetime import datetime
# class Employee:
#
#     name = 'python'
#
#     def printName(self):
#         print(self)
#         print(self.name)
#
# e1 = Employee()
# e2 = Employee()
# print(Employee.name)
# e1.printName()
#
# # def e.printName():
#
# # for i in range(100):
# #     e = Employee()
# #     e.insertInDB()

# Fraction = num / den
# 1 / 2 + 2 / 3 = (6 + 3) / 6 = 9 / 6 (= 3 / 2)
class Fraction(object):

    num = 0
    den = 1
    # Constructor
    def __init__(self, x, y):
        self.num = x
        self.den = y

        assert type(self.num) == int and type(self.den) == int

    def __add__(self, b):
        try:
            self.den = self.den * b.den
            self.num = (self.den // self.num) + (self.den // b.num)

        except ZeroDivisionError as e: # if division by zero, set fraction to 0
            print('exception' , e)
            self.num = 0
            self.den = 1

        finally:
            return self

    def __str__(self): # human readable representation of class
        return "str : <{0} / {1}>".format(self.num, self.den)

    def __repr__(self): # detailed representation of class
        return "repr : <{0} / {1}>".format(self.num, self.den)

    def printHi(self):
        print('Hi I am a fraction')

'''
# Inheritance
class NormalizedFraction(Fraction):

    def __init__(self, x, y):
        self.num = x
        self.den = y
        g = math.gcd(self.num, self.den) # GCD : greatest common divisor
        self.num = self.num // g
        self.den = self.den // g
        assert type(self.num) == int and type(self.den) == int
'''

f1 = Fraction(0, 1)
f2 = Fraction(2, 3)
f1 = f1 + f2
# print(f1.num, ' ', f1.den)
# f1.printHi()
print(repr(f1))
print(str(f1))
# print('{0} / {1}'.format(f1.num, f1.den))

# f3 = NormalizedFraction(9, 6)
# f4 = NormalizedFraction(3, 2)
# print(f3)
# print(f4)
# f3 = f3 + f4
# print(f3)

'''
## Class decorator

def my_logger(orig_func):
    import logging
    logging.basicConfig(filename='{}.log'.format(orig_func.__name__), level=logging.INFO)

    def wrapper(*args, **kwargs):
        logging.info('Ran with args: {}, and kwargs: {}'.format(args, kwargs)
                     )
        return orig_func(args, kwargs)

    return wrapper

@my_logger
def display_info(name, age):
    print('display_info ran with arguments {}, {}'.format(name, age))

display_info('John', 25)

'''
## static and class methods

# class Employee:
# 
#     num_of_emps = 0
#     raise_amount = 1.04
# 
#     def __init__(self, first, last, pay):
#         self.first = first
#         self.last = last
#         self.email = first + '.' +  last + '@email.com'
#         self.pay = pay
# 
#     def fullname(self):
#         return '{} {}'.format(self.first, self.last)
# 
#     def apply_raise(self):
#         self.pay = int(self.pay * self.raise_amount)
# 
#     @classmethod
#     def set_raise_amount(cls, amount):
#         cls.raise_amount = amount
# 
# 
# emp_1 = Employee('Prateep', 'Mukherjee', 50000)
# emp_2 = Employee('Ab','Cd', 60000)
# 
# Employee.set_raise_amount(1.05)
# 
# print(Employee.raise_amount)
# print(emp_1.raise_amount)
# print(emp_2.raise_amount)


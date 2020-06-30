# print("hello world")
#
# if 5 > 2:
#     print('hi')
#
# x = 5
# print(type(x))
# x = "John"
# print(type(x))
#
# x = "Python is "
# y = "awesome"
# z =  x + y
# print(z)
#
# print(type(5 // 2))


thislist = ["apple", "banana", "cherry"]
thislist.pop(1)
print(thislist)


# Arithmetic Operators

# Assignment Operators

# Comparison Operators

# Logical Operators

# Bitwise Operators

# Identity Operators
# x = 5
# print(x is 5)
# print(x is not 5)
#
#
# # Membership Operators
#
# def f(fname="prateep"):
#     print(fname + " Refsns")
#
# f("Emil")
# f("Toias")
# f()
#
# def bmi_calculator(name, weight_kg, height_m):
#     bmi = weight_kg / (height_m ** 2)
#     print("Hello {0}, your bmi is {1:0.3f} kg/m^2".format(name, bmi))
#     return bmi
#
# print(bmi_calculator.__dict__)
# bmi_calculator("pp", 85, 2)
# # print('name {}'.format(bmi_calculator.__name__))

## Decorator
"""
decorator example
"""
# def decofn(orifn):
#     def wrapperfn(*args, **kwargs):
#         # print('wrapper {}'.format(orifn.__name__))
#         return orifn(*args, **kwargs)
#     return wrapperfn
#
# def display():
#     print("display ran")
#
# display_decorated = decofn(display)
# display_decorated()

# @decofn
# def display_info(name, age):
#     print("display ran with arguments {}, {}".format(name, age))

# display_info(name="John", age=25)
#
# a = [1,2,3]
# # print(*a)

# def student_info(*args, **kwargs):
#     print(len(args))
#     print(len(kwargs))

# courses = {'Art', 'English'}
# info = {'name' : 'John', 'age' : 22}
# student_info(*courses, **info)
#

# class A(object):
#     total = 0
#
#     def __init__(self):
#         self.total += 1
#
#     @staticmethod
#     def status():
#         print("Total A", A.total)
#
# a = A()
# print(A.total)
# print(a.total)
# a.total += 1
# print(a.total)
# print(isinstance(a,A))
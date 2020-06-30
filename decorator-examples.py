## Decorator
"""
decorator example
"""
# def decofn(orifn):
#     def wrapperfn(*args, **kwargs):
#         print('wrapper {}'.format(orifn.__name__))
#         return orifn(*args, **kwargs)
#     return wrapperfn
#
# @decofn
# def greet(name, age):
#     print("Hi {}, your age is {}".format(name, age))
#
# greet_decorated = decofn(greet)
# greet_decorated('John', 26)
# # greet('John', 25)


# def hello_decorator(func):
#     # inner1 is a Wrapper function in
#     # which the argument is called
#
#     # inner function can access the outer local
#     # functions like in this case "func"
#     def wrapperfn():
#         print("Hello, this is before function execution")
#
#         # calling the actual function now
#         # inside the wrapper function.
#         func()
#
#         print("This is after function execution")
#
#     return wrapperfn()
#
# @hello_decorator
# # defining a function, to be called inside wrapper
# def function_to_be_used():
#     print("This is inside the function !!")
#
#
# # passing 'function_to_be_used' inside the
# # decorator to control its behavior
# function_to_be_used #= hello_decorator(function_to_be_used)
#
# import time
# # import logging
# def calculate_time(fn):
#
#     def wrapperfn(*args, **kwargs):
#         tstart = time.clock()
#         # logger = logging.basicConfig()
#         ret = fn(*args, **kwargs)
#         tend = time.clock()
#         print('{0} took {1:0.3f} seconds'.format(fn.__name__, tend - tstart))
#         return ret
#
#     return wrapperfn
#
# @calculate_time
# def factorial(num):
#     fact = 1
#     for i in range(1,num+1):
#         fact *= i
#     return fact
#
# ans = factorial(50)
# print(ans)
#

class decorator(object):

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *args):
        print('Calling {func} with args {args}'.format(func=self.fn.__name__, args=args))
        return self.fn(*args)

@decorator
def func(x,y):
    return x,y

# func_decorated = decorator(func)

print(func(1,2))
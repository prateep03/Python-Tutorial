'''
    Three types of methods in a class:
        - regular method : user defined, first attribute self
        - buitin methods : language designer defined, first attribute self
        - static/class-methods : user defined, first attribute may or may not be self
'''

class Employee(object):

    raise_amt = 1.04

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.email = first + '.' + last + '@email.com'
        self.pay = pay

    def fullname(self):
        # print(self.first + ' ' + self.last)
        return '{0} {1}'.format(self.first, self.last)

    def apply_raise(self):
        self.pay = int(self.pay * self.raise_amt)

    '''
       Class method, used to change attributes of class
       First argument is cls
    '''
    @classmethod
    def set_raise_amt(cls, amt):
        cls.raise_amt = amt
        return cls

    ''' Static method, does not use class methods/attributes.
        Therfore no self as first argument
    '''
    @staticmethod
    def greet():
        print('Hi')

emp_1 = Employee('John','Smith', 50000)
emp_2 = Employee('Will','Smith', 60000)

Employee.set_raise_amt(1.15)

emp_1.greet()
print(emp_1.pay)
print(emp_1.raise_amt)
# emp_1.apply_raise()
print(emp_1.pay)

print(emp_2.pay)
print(emp_2.raise_amt)
emp_2.apply_raise()
print(emp_2.pay)
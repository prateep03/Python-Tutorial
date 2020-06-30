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

    def __add__(self, other):
        if isinstance(other, Employee):
            return self.pay + other.pay
        else:
            return -1

    def __repr__(self):
        ''' Representation of the class for developers '''
        # print('first->{}, last->{}, pay->{}'.format(self.first, self.last, self.pay))
        return 'first->{}, last->{}, pay->{}'.format(self.first, self.last, self.pay)

    def __str__(self):
        ''' Human readable representation of the class '''
        return self.fullname()

emp_1 = Employee('John','Smith', 50000)
emp_2 = Employee('Will','Smith', 60000)
print(emp_1 + emp_2)

print(repr(emp_1))
print(str(emp_1))

# print(emp_1.fullname())
# print('original pay', emp_1.pay)
# emp_1.apply_raise()
# print('raise pay', emp_1.pay)

class Developer(Employee):

    def __init__(self, first, last, pay, prog_lang):
        super(Developer, self).__init__(first, last, pay)
        self.prog_lang = prog_lang


# dev_1 = Developer('Will', 'Smith', 60000, 'Python')
# print(dev_1.email)
# print(dev_1.fullname())

class Manager(Employee):

    def __init__(self, first, last, pay, employees =  None):
        super(Manager, self).__init__(first, last, pay)
        if employees is None:
            self.employees = []
        else:
            self.employees = employees

    def add_emp(self, emp):
        if emp not in self.employees:
            self.employees.append(emp)

    def remove_emp(self, emp):
        if emp in self.employees:
            self.employees.remove(emp)

    def print_employees(self):
        for emp in self.employees:
            print('-->', emp.fullname())
        return 1


print(dir(Manager))

dev_1 = Developer('John', 'Smith', 50000, 'Python')
dev_2 = Developer('Will', 'Smith', 60000, 'Java')

# print(repr(dev_1))
# print(issubclass(Developer, Manager))
# mgr_1 = Manager('Jack', 'Roy', 90000, [dev_1])
# print(mgr_1.fullname())
# mgr_1.print_employees()
# print('Adding employee')
# mgr_1.add_emp(dev_2)
# mgr_1.print_employees()
# mgr_1.remove_emp(dev_2)
# print('Removing employee')
# mgr_1.print_employees()
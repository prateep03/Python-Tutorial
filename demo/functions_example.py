print('Importing module...')

'''
 - passing parameters by values
'''
def print_student_info(name, courses, sem, univ='Rutgers'):

    print('Hi ', name)
    # print(courses)
    print(sem)
    print(univ)

    for c in courses:
        print(c)

# print_student_info('prateep', ['Maths', 'CompSci'], 'Fall', 'UoC')
# print_student_info('john', ['Arts', 'Physics'], 'Spring')

'''
 - passing parameters by references (address of the values)
'''

# print('--------------------------------------')

def print_student_info_2(*args, **kwargs): # kwargs - key-word arguments
    print('args = ', args)
    print(type(args))
    print('kawrgs = ', kwargs)

# print_student_info_2(['Maths', 'CompSci'], name ='John', age = 23)

# courses = ['Maths', 'CompSci']
# info = {'name' : 'John', 'age' : 23}

# print_student_info_2(*courses, **info)
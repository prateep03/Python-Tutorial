student = {'name': 'John', 'age': 25, 'courses': ['Math', 'CompSci']}

# student['phone'] = '123456'
# student['name'] = 'James'

# print(student.get('phone', 'Not Found'))

# student.update({'name': 'Prateep', 'age': 26, 'phone': '123456'})

# Delete key.
# 1.
# del student['age']

# 2.
# age = student.pop('age')

# print(student)
# print(age)

# print(len(student))

# print(student.keys())
# print(student.values())
# print(student.items())

for key, value in student.items():
    print(key, value)

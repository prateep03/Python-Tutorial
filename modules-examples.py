import sys

sys.path.append('D:\\Teaching\\demo')

import functions_example as fe

from functions_example import print_student_info_2 as ps2, print_student_info

# functions_example.print_student_info()
# functions_example.print_student_info_2()
ps2(['Maths', 'CompSci'], name='john', age=23)

# access functions by modulename.functioname
import os
import sys
import shutil

# print('I said, \"hi\" good monrning')

# print(os.getcwd()) # cwd ->> current working directory

# os.chdir('D:\\Teaching\\demo')
#
# print(os.getcwd()) # cwd ->> current working directory

# print(sys.path)

# privilege access to folder
#   owner - one who creates the directory
#   group - team that owner belongs to
#   rest - anyone else
#  777, 744, 755
# if not os.path.exists('demo2'):
#     os.mkdir('demo2') # r - read(4), w - write(2), x - execute(1)
#                 # 6 => read + write
#                 # 7 => read + write + execute
#                 # 5 => read + execute
#     os.makedirs('demo2\\demo3')
#
# os.removedirs('demo2\\demo3')

# for f in os.listdir(os.getcwd()):
#     if not os.path.isdir(f):
#         print(f)

# present directory - .
# parent directory  - ..
# for item in os.listdir('D:\\Teaching\\demo'):
#     if os.path.isdir(item):
#         continue
#     if item.endswith('.csv'):
#         srcpath = os.path.join( 'D:\\Teaching\\demo', item)
#         dstpath = 'D:\\Teaching'
#         shutil.move( srcpath, dstpath)
#     # print(os.path.basename(item))

for dirpath, dirname, filenames in os.walk('D:\\Teaching\\demo'):
    print('Dir path ', dirpath)
    print('Dir name ', dirname)
    print('File names ', filenames)

# file pointer - fp
fp = open('syllabus.txt','r')
print(fp)
print(fp.read(10))
print(fp.read(10))

print(fp.tell()) # to check current position of reader

fp.seek(0)

print(fp.tell())

fp.close()
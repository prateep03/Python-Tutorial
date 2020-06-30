import re

txt = """
       -
       123-555-7777
       344-897-1456
       080-119-72134
      """

emails = """
    abc@gmail.com
    abc.D@nyu.edu
    abc.9@yahoomail.com
"""
# txt2 = ""
# txt2 = "Temperature in Hyderabad is 10 degrees"

# match returns objects at the beginning of string
# x = re.match("The", txt)
# print("match ", x)

# search returns objects first match
# x = re.search("\w", txt2)
# print(x, "---")

# findall returns iterator of matched strings
iter_x = re.finditer(r"[a-zA-Z.0-9]+@(\w+|)\.(\w+)", emails)
count = 0
for x in iter_x:
    if x is not None:
        print(x, x.group(1), x.group(2))
        count += 1
print("Number of matches {}".format(count))

# str = "The rain in Spain"
# x = re.split("\s", str, 1)
# print(x) # 'The, rain, in, Spain'
# lst_str = ' '.join(x)
# print(lst_str)

# str = "The rain in Singapore and Spain"
# x = re.finditer(r"\bS\w+", str)
# print(x)
# # print(x.string)
#
# for xx in x:
#     print(repr(xx))
#     # print(xx.string)
#     print(xx.group(0))
import requests
from xml.etree import ElementTree as ET

# https://www.geeksforgeeks.org/xml-parsing-python/
# get the file from http
def loadRSS():
    # url of rss feed
    url = 'http://www.hindustantimes.com/rss/topnews/rssfeed.xml'

    # creating HTTP response object from given url
    resp = requests.get(url)

    # saving the xml file
    with open('topnewsfeed.xml', 'wb') as f:
        f.write(resp.content)

# main parser
def parseXML(xmlfile):

    tree = ET.parse(xmlfile)
    # print(tree)

    # root element
    root = tree.getroot()
    print(root, "->", root.attrib)
    tags = tree.findall("country")
    print(tags)
    for child in tags:
        print('name ->{}'.format(child.attrib))
        for tag in child:
            print(tag.tag, end=' ')
            if tag.text is None:
                print(tag.attrib)
            else:
                print(tag.text)
        print('------------------')

if __name__ == "__main__":
    # loadRSS()

    parseXML('topnewsfeed.xml')
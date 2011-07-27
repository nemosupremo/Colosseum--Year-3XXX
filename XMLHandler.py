import xml.sax

class XMLNode(object):
    attrs = {}
    data = []
    parent = None
    children = []
    name = ""
    data = ""

    def __init__(self, name, parent=None, children=[], data = ""):
        self.name = name
        self.parent = parent
        self.children = list(children)
        self.attrs = dict({})

    def setAttr(self, key, val):
        self.attrs[key] = val

    def getAttr(self, key):
        return self.attrs[key]

    def __getitem__(self, key):
        return self.attrs[key]
        
    def __setitem__(self, key, val):
        self.attrs[key] = val

    def addChild(self, child):
        self.children.append(child)

    def getChildren(self):
        return self.children

    def setData(self, data):
        self.data = data

    def getData(self):
        return self.data

    def setParent(self, parent):
        self.parent = parent
    
    def getParent(self):
        return self.parent
    
    
 
class XMLHandler(xml.sax.handler.ContentHandler):
    root = {}

    parentTag = {}
    buff = ""
    parentMap = None
    buffMapping = None
    def __init__(self):
        self.inTitle = 0
        self.root = XMLNode("root")
        #{'children':[], 'parent':None}
        self.parentMap = self.root

    def startElement(self, name, attributes):
        self.buffMapping = XMLNode(name, self.parentMap)
        #print self.buffMapping.name, "has parent", self.parentMap.name
        #print "A", name
        #print "\tB", self.parentMap.name
        #self.buffMapping['parent'] = self.parentMap
        self.buff = ""
        for attr in attributes.getNames():
            self.buffMapping[str(attr)] = str(attributes[attr])
        self.parentMap.addChild(self.buffMapping)
        #print "Adding child %s to parent %s" % (self.buffMapping.name, self.parentMap.name) 
        self.parentMap = self.buffMapping
        #print "Setting parent to", self.parentMap.name

    def characters(self, data):
        self.buff += data

    def endElement(self, name):
        if name != self.buffMapping.name:
            self.buffMapping = self.buffMapping.getParent()
        #print "end", name
        #print "end", self.buffMapping.name
        self.buffMapping.setData(str(self.buff).strip())
        self.parentMap = self.buffMapping.getParent()
        #print "Set parent to", self.parentMap.name

    def parse(self, filen):
        parser = xml.sax.make_parser(  )
        parser.setContentHandler(self)
        parser.parse(filen)

    def getMap(self):
        return self.root.getChildren()[0]


if __name__ == "__main__":
    wh = XMLHandler()
    f = raw_input("File:")
    wh.parse(f)
    print wh.getMap()
    raw_input()

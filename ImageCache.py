class ImageCache(object):
    loadedImages = {}
    loadFunc = None

    def __init__(self, loadFunc = None):
        self.loadedImages = {}
        self.loadFunc = loadFunc

    def setLoadFunc(self, func):
        self.loadFunc = func

    def loadImage(self, filename):
        if filename in self.loadedImages:
            return self.loadedImages[filename]
        else:   
            self.loadedImages[filename] = self.loadFunc(filename)
            return self.loadedImages[filename]
        
    def clear(self):
        self.loadedImages.clear()

    def hasImage(self, imagepath):
        return self.loadedImages.has_key(imagepath)
        
    def __getitem__(self, filename):
        return self.loadImage(filename)
        
    def __setitem__(self, key, value):
        self.loadedImages[key] = value

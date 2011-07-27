class SoundCache(object):
    loadedSounds = {}
    loadFunc = None

    def __init__(self, loadFunc = None):
        self.loadedImages = {}
        self.loadFunc = loadFunc

    def setLoadFunc(self, func):
        self.loadFunc = func

    def loadSound(self, filename):
        if filename in self.loadedSounds:
            return self.loadedSounds[filename]
        else:   
            self.loadedSounds[filename] = self.loadFunc(filename)
            return self.loadedSounds[filename]
        
    def clear(self):
        self.loadedSounds.clear()

    def hasSound(self, soundPath):
        return self.loadedSounds.has_key(soundPath)
        
    def __getitem__(self, filename):
        return self.loadSound(filename)
        
    def __setitem__(self, key, value):
        self.loadedSounds[key] = value

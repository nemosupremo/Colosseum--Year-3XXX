import Scene
import UI
import util
import pygame
import GameClient
import time
import random

class TitleScene(Scene.Scene):

    errorMessage = ""
    renderedErrorMsg = None
    displayConnect = True
    displayGraphic = False
    handles = [GameClient.CALL_ROOMLIST,GameClient.CALL_PLAYERLIST]
    loading = False
    loadingAnim = 0
    dots = 0
    errorFont = None

    def createHandleFunctions(self):
        self.handleFunc = {
            GameClient.CALL_ROOMLIST : self.connectSuccess,
            GameClient.CALL_PLAYERLIST : self.connectSuccess
        }

    def setUp(self):
        self.errorFont = pygame.font.Font(None, 24)
        util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'title.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'name.png')]
        util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'server.png')]
        self.nameTxt = UI.TextInput(500, None, 46, 300, 350)
        self.serverTxt = UI.TextInput(500, None, 46, 300, 390)

        self.nameTxt.setText("player%d" % random.randint(10000, 99999))
        self.serverTxt.setText("localhost")
        
        self.connButton = UI.Button(util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'connect.png')],
                                    util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'connect_over.png')],
                                    660, 430)
        self.connButton.setOnClick(self.doConnect)

        self.MAIN.eventManager.addHandler(self.nameTxt)
        self.MAIN.eventManager.addHandler(self.serverTxt)
        self.MAIN.eventManager.addHandler(self.connButton)
        
        self.MAIN.cam.addOverlay(self.nameTxt)
        self.MAIN.cam.addOverlay(self.serverTxt)
        self.MAIN.cam.addOverlay(self.connButton)
        self.MAIN.cam.addOverlay(self)
        
        if self.errorMessage != "":
            self.renderedErrorMsg = self.errorFont.render(self.errorMessage, True, (255,0,0))
        super(TitleScene, self).setUp()

    def connectVisible(self, visible):
        self.connButton.setVisible(visible)

    def setLoading(self, l):
        self.loading = l

    def doConnect(self):
        self.MAIN.connect(self.nameTxt.getText(), self.serverTxt.getText())

    def connectSuccess(self, *args):
        pass

    def destroy(self):
        self.MAIN.cam.removeOverlay(self.nameTxt)
        self.MAIN.cam.removeOverlay(self.serverTxt)
        self.MAIN.cam.removeOverlay(self.connButton)
        self.MAIN.cam.removeOverlay(self)

        self.MAIN.eventManager.removeHandler(self.nameTxt)
        self.MAIN.eventManager.removeHandler(self.serverTxt)
        self.MAIN.eventManager.removeHandler(self.connButton)
        
        del self.nameTxt
        del self.serverTxt
        del self.connButton
        del self.errorFont
        util.IMAGECACHE.clear()
        super(TitleScene, self).destroy()

    def setErrorMessage(self, msg):
        self.errorMessage = msg
        if msg == "":
            self.renderedErrorMsg = None
        else:
            self.renderedErrorMsg = self.errorFont.render(self.errorMessage, True, (255,0,0))

    def draw(self, surface, offset=(0,0)):
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'title.png')], (0,0))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'name.png')], (100,350))
        surface.blit(util.IMAGECACHE[util.getFile(util.IMAGES, "TITLE", 'server.png')], (100,390))
        if self.loading:
            if time.time() > self.loadingAnim:
                self.dots += 1
                if self.dots > 3:
                    self.dots = 0
                txt = "Loading" + "."*self.dots
                self.renderedErrorMsg = self.errorFont.render(txt, True, (255,0,0))
                self.loadingAnim = time.time() + .25
        if self.renderedErrorMsg != None:
            surface.blit(self.renderedErrorMsg, (100, 300))

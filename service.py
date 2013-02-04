#
# This Program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
# 
# This Program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# http://www.gnu.org/copyleft/gpl.html
# 

### import modules
import xbmc
import xbmcaddon

### import libraries
from xmlrpclib import ServerProxy

### get addon info
__addon__       = xbmcaddon.Addon(id='service.nzbget')
__addonid__     = __addon__.getAddonInfo('id')
__addonname__   = __addon__.getAddonInfo('name')
__version__     = __addon__.getAddonInfo('version')
# __author__      = __addon__.getAddonInfo('author')
# __addonpath__   = __addon__.getAddonInfo('path')
# __addonprofile__= xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
# __icon__        = __addon__.getAddonInfo('icon')
# __localize__    = __addon__.getLocalizedString

__SLEEP_TIME__ = 1000

class NZBGet():

    isDownloadPaused = False
    isPauseRegister1 = False
    isPostProcessingPaused = False
    isScanPaused = False

    def pause(self, isPlayingVideo):
        controlNzbget = __addon__.getSetting('controlNzbget') # can be either 'Audio', 'Video' or 'Audio or Video'
        pauseWhenAudio = controlNzbget.startswith('Audio')    # catches both 'Audio' and 'Audio or Video'
        pauseWhenVideo = controlNzbget.endswith('Video')      # catches both 'Video' and 'Audio or Video'

        if ((isPlayingVideo and pauseWhenVideo) or (not isPlayingVideo and pauseWhenAudio)):
            username = __addon__.getSetting('username')
            password = __addon__.getSetting('password')
            hostname = __addon__.getSetting('hostname')
            port = __addon__.getSetting('port')
            pauseDownload = __addon__.getSetting('pauseDownload')
            pausePostProcessing = __addon__.getSetting('pausePostProcessing')
            pauseScan = __addon__.getSetting('pauseScan')
            self.isPauseRegister1 = __addon__.getSetting('pauseRegister') == '1'

            server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

            if (pauseDownload):
                if (self.isPauseRegister1):
                    server.pausedownload()
                else:
                    server.pausedownload2()
                self.isDownloadPaused = True
                log('Pause downloading')

            if (pausePostProcessing):
                self.isPostProcessingPaused = True            
                server.pausepost()
                log('Pause post processing')

            if (pauseScan):
                server.pausescan()
                self.isScanPaused = True
                log('Pause scanning of incoming nzb-directory')

    def resume(self):
        username = __addon__.getSetting('username')
        password = __addon__.getSetting('password')
        hostname = __addon__.getSetting('hostname')
        port = __addon__.getSetting('port')

        server = ServerProxy('http://%s:%s@%s:%s/xmlrpc' % (username, password, hostname, port))

        if (self.isDownloadPaused):
            if (self.isPauseRegister1):
                server.resumedownload()
            else:
                server.resumedownload2()
            self.isDownloadPaused = False
            log('Resume downloading')

        if (self.isPostProcessingPaused):
            server.resumepost()
            self.isPostProcessingPaused = False
            log('Resume post processing')

        if (self.isScanPaused):
            server.resumescan()
            log('Resume scanning of incoming nzb-directory')


class NZBGetService(xbmc.Player):

    def __init__(self):
        xbmc.Player.__init__(self)
        self.nzbget = NZBGet() 

    def onPlayBackStarted(self):
        self.nzbget.pause(self.isPlayingVideo())

    def onPlayBackEnded(self):
        self.nzbget.resume()

    def onPlayBackStopped(self):
        self.nzbget.resume()

#    def onPlayBackPaused(self):
#        not used by this service        
            
#    def onPlayBackResumed(self):
#        not used by this service


def log(message):
    xbmc.log(__addonid__ + ': ' + message)


if (__name__ == "__main__"):

    log('Starting: ' + __addonname__ + ' v' + __version__)
    nzbget = NZBGetService()
    while (not xbmc.abortRequested):
        xbmc.sleep(__SLEEP_TIME__)

    log('Stopped: ' + __addonname__ + ' v' + __version__)


from uServerRoutes import uServerRoutes
from uClient import uClient
from os import stat
try:
    import usocket as socket
except:
    import socket
# import gc
import re


class uWebServer:

    _indexPages = [
        "index.html",
        "default.html",
    ]

    _mimeTypes = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".ico": "image/x-icon"
    }

    _html_escape_chars = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;"
    }

    @staticmethod
    def HTMLEscape(s):
        return ''.join(uWebServer._html_escape_chars.get(c, c) for c in s)

    # def _tryAllocByteArray(size):
    #     for x in range(10):
    #         try:
    #             gc.collect()
    #             return bytearray(size)
    #         except:
    #             pass
    #     return None

    @staticmethod
    def _fileExists(path):
        try:
            stat(path)
            return True
        except:
            return False

    def __init__(self,
                 routeHandlers=[],
                 port=80,
                 bindIP='0.0.0.0',
                 webPath="/www"):

        self._srvAddr = (bindIP, port)
        self._webPath = webPath
        self._notFoundUrl = None
        self._started = False

        self.MaxWebSocketRecvLen = 1024
        self.WebSocketThreaded = True
        self.AcceptWebSocketCallback = None
        self.LetCacheStaticContentLevel = 2

        self._routeHandlers = []
        for route, method, func in routeHandlers:
            routeParts = route.split('/')
            # -> ['', 'users', '<uID>', 'addresses', '<addrID>', 'test', '<anotherID>']
            routeArgNames = []
            routeRegex = ''
            for s in routeParts:
                if s.startswith('<') and s.endswith('>'):
                    routeArgNames.append(s[1:-1])
                    routeRegex += '/(\\w*)'
                elif s:
                    routeRegex += '/' + s
            routeRegex += '$'
            # -> '/users/(\w*)/addresses/(\w*)/test/(\w*)$'
            routeRegex = re.compile(routeRegex)

            self._routeHandlers.append(uServerRoutes(route, method, func, routeArgNames, routeRegex))

    def _serverProcess(self):
        self._started = True
        while True:
            try:
                client, cliAddr = self._server.accept()
                print(client)
                print(cliAddr)
            except Exception as ex:
                print(ex)
                if ex.args and ex.args[0] == 113:
                    break
                continue
            uClient(self, client, cliAddr)
        self._started = False
        print('end on socket loop')

    def Start(self):
        if not self._started:
            print('open socket')
            self._server = socket.socket()
            self._server.setsockopt(socket.SOL_SOCKET,
                                    socket.SO_REUSEADDR,
                                    1)
            self._server.bind(self._srvAddr)
            self._server.listen(1)
            self._serverProcess()
        print('end on socket loop')

    def Stop(self):
        if self._started:
            self._server.close()

    def SetNotFoundPageUrl(self, url=None):
        self._notFoundUrl = url

    def GetMimeTypeFromFilename(self, filename):
        filename = filename.lower()
        for ext in self._mimeTypes:
            if filename.endswith(ext):
                return self._mimeTypes[ext]
        return None

    def GetRouteHandler(self, resUrl, method):
        if self._routeHandlers:
            # resUrl = resUrl.upper()
            if resUrl.endswith('/'):
                resUrl = resUrl[:-1]
            method = method.upper()
            for rh in self._routeHandlers:
                if rh.method == method:
                    m = rh.routeRegex.match(resUrl)
                    if m:  # found matching route?
                        if rh.routeArgNames:
                            routeArgs = {}
                            for i, name in enumerate(rh.routeArgNames):
                                value = m.group(i + 1)
                                try:
                                    value = int(value)
                                except:
                                    pass
                                routeArgs[name] = value
                            return (rh.func, routeArgs)
                        else:
                            return (rh.func, None)
        return (None, None)

    def _physPathFromURLPath(self, urlPath):
        if urlPath == '/':
            for idxPage in self._indexPages:
                physPath = self._webPath + '/' + idxPage
                if uWebServer._fileExists(physPath):
                    return physPath
        else:
            physPath = self._webPath + urlPath
            if uWebServer._fileExists(physPath):
                return physPath
        return None

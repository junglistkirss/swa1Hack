from json import loads
# try:
#     import usocket as socket
# except:
#     import socket
# import gc
from uResponse import uResponse


class uClient:

    def __init__(self, uWebServer, socket, addr):
        socket.settimeout(2)
        self._uWebServer = uWebServer
        self._socket = socket
        self._addr = addr
        self._method = None
        self._path = None
        self._httpVer = None
        self._resPath = "/"
        self._queryString = ""
        self._queryParams = {}
        self._headers = {}
        self._contentType = None
        self._contentLength = 0

        self._processRequest()

    def _processRequest(self):
        try:
            response = uResponse(self)
            if self._parseFirstLine(response):
                if self._parseHeader(response):
                    upg = self._getConnUpgrade()
                    if not upg:
                        routeHandler, routeArgs = self._uWebServer.GetRouteHandler(self._resPath, self._method)
                        if routeHandler:
                            if routeArgs is not None:
                                print('handle route args')
                                routeHandler(self, response, routeArgs)
                            else:
                                print('handle route')
                                routeHandler(self, response)
                        elif self._method.upper() == "GET":
                            filepath = self._uWebServer._physPathFromURLPath(self._resPath)
                            if filepath:
                                contentType = self._uWebServer.GetMimeTypeFromFilename(filepath)
                                if contentType:
                                    if self._uWebServer.LetCacheStaticContentLevel > 0:
                                        if self._uWebServer.LetCacheStaticContentLevel > 1 and 'if-modified-since' in self._headers:
                                            response.WriteResponseError(304)
                                        else:
                                            headers = {'Last-Modified': 'Dim, 18 Nov 2018 23:42:00 GMT', 'Cache-Control': 'max-age=86400'}
                                            response.WriteResponseFile(filepath, contentType, headers)
                                    else:
                                        response.WriteResponseFile(filepath, contentType)
                                else:
                                    response.WriteResponseError(403)
                            else:
                                response.WriteResponseNotFound()
                        else:
                            response.WriteResponseError(405)
                    else:
                        response.WriteResponseError(501)
                else:
                    response.WriteResponseError(400)
        except:
            response.WriteResponseError(500)
        try:
            print('close client socket')
            self._socket.close()
        except:
            pass

    @staticmethod
    def _unquote_decode(data):
        i = 0
        ret = bytearray()
        while i < len(data):
            c = ord(data[i])
            if c == 0x25:  # '%'
                try:
                    c = int(data[i + 1:i + 3], 16)
                    i += 2  # skip next 2 bytes
                except:
                    pass
            elif c == 0x2B:  # '+'
                c = 0x20  # ' '
            ret.append(c)
            i += 1

        return str(ret, "utf-8")

    def _parseFirstLine(self, response):
        try:
            elements = self._socket.readline().decode().strip().split()
            if len(elements) == 3:
                self._method = elements[0].upper()
                self._path = elements[1]
                self._httpVer = elements[2].upper()
                elements = self._path.split('?', 1)
                if len(elements) > 0:
                    self._resPath = self._unquote_decode(elements[0])
                    if len(elements) > 1:
                        self._queryString = elements[1]
                        elements = self._queryString.split('&')
                        for s in elements:
                            param = s.split('=', 1)
                            if len(param) > 0:
                                value = self._unquote_decode(param[1]) if len(param) > 1 else ''
                                self._queryParams[self._unquote_decode(param[0])] = value
                return True
        except Exception as ex:
            print(ex)
        return False

    def _parseHeader(self, response):
        while True:
            elements = self._socket.readline().decode().strip().split(':', 1)
            if len(elements) == 2:
                self._headers[elements[0].strip().lower()] = elements[1].strip()
            elif len(elements) == 1 and len(elements[0]) == 0:
                if self._method == 'POST' or self._method == 'PUT':
                    self._contentType = self._headers.get("content-type", None)
                    self._contentLength = int(self._headers.get("content-length", 0))
                return True
            else:
                return False

    def _getConnUpgrade(self):
        if 'upgrade' in self._headers.get('connection', '').lower():
            return self._headers.get('upgrade', '').lower()
        return None

    def ReadRequestContent(self, size=None):
        self._socket.setblocking(False)
        b = None
        try:
            if not size:
                b = self._socket.read(self._contentLength)
            elif size > 0:
                b = self._socket.read(size)
        except:
            pass
        self._socket.setblocking(True)
        return b if b else b''

    def ReadRequestPostedFormData(self):
        res = {}
        data = self.ReadRequestContent()
        if len(data) > 0:
            elements = data.decode().split('&')
            for s in elements:
                param = s.split('=', 1)
                if len(param) > 0:
                    value = self._unquote_decode(param[1]) if len(param) > 1 else ''
                    res[self._unquote_decode(param[0])] = value
        return res

    def ReadRequestContentAsJSON(self):
        try:
            return loads(self.ReadRequestContent())
        except:
            return None

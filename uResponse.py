from json import dumps
from os import stat
# try:
#     import usocket as socket
# except:
#     import socket
# import gc
# import re


class uResponse:

    def __init__(self, client):
        self._client = client

    def _write(self, data):
        if data:
            if type(data) == str:
                data = data.encode()
            return self._client._socket.write(data)
        return 0

    def _writeFirstLine(self, code):
        reason = self._responseCodes.get(code, ('Unknown reason', ))[0]
        self._write("HTTP/1.1 %s %s\r\n" % (code, reason))

    def _writeHeader(self, name, value):
        self._write("%s: %s\r\n" % (name, value))

    def _writeContentTypeHeader(self, contentType, charset=None):
        if contentType:
            ct = contentType + (("; charset=%s" % charset) if charset else "")
        else:
            ct = "application/octet-stream"
        self._writeHeader("Content-Type", ct)

    def _writeServerHeader(self):
        self._writeHeader("Server", "uServer")

    def _writeEndHeader(self):
        self._write("\r\n")

    def _writeBeforeContent(self, code, headers, contentType, contentCharset, contentLength):
        self._writeFirstLine(code)
        if isinstance(headers, dict):
            for header in headers:
                self._writeHeader(header, headers[header])
        if contentLength > 0:
            self._writeContentTypeHeader(contentType, contentCharset)
            self._writeHeader("Content-Length", contentLength)
        self._writeServerHeader()
        self._writeHeader("Connection", "close")
        self._writeEndHeader()

    def WriteResponse(self, code, headers, contentType, contentCharset, content):
        try:
            if content:
                if type(content) == str:
                    content = content.encode()
                contentLength = len(content)
            else:
                contentLength = 0
            self._writeBeforeContent(code, headers, contentType, contentCharset, contentLength)
            if content:
                self._write(content)
            return True
        except:
            return False

    def WriteResponseFile(self, filepath, contentType=None, headers=None):
        try:
            size = stat(filepath)[6]
            if size > 0:
                with open(filepath, 'rb') as file:
                    self._writeBeforeContent(200, headers, contentType, None, size)
                    buf = bytearray(1024)
                    # buf = uWebServer._tryAllocByteArray(1024)
                    if buf:
                        while size > 0:
                            x = file.readinto(buf)
                            if x < len(buf):
                                buf = memoryview(buf)[:x]
                            self._write(buf)
                            size -= x
                        return True
                    self.WriteResponseInternalServerError()
                    return False
        except:
            pass
        self.WriteResponseNotFound()
        return False

    def WriteResponseFileAttachment(self, filepath, attachmentName, headers=None):
        if not isinstance(headers, dict):
            headers = {}
        headers["Content-Disposition"] = "attachment; filename=\"%s\"" % attachmentName
        return self.WriteResponseFile(filepath, None, headers)

    def WriteResponseOk(self, headers=None, contentType=None, contentCharset=None, content=None):
        return self.WriteResponse(200, headers, contentType, contentCharset, content)

    def WriteResponseJSONOk(self, obj=None, headers=None):
        return self.WriteResponse(200, headers, "application/json", "UTF-8", dumps(obj))

    def WriteResponseRedirect(self, location):
        headers = {"Location": location}
        return self.WriteResponse(302, headers, None, None, None)

    def WriteResponseError(self, code):
        responseCode = self._responseCodes.get(code, ('Unknown reason', ''))
        return self.WriteResponse(code,
                                  None,
                                  "text/html",
                                  "UTF-8",
                                  self._msgTmpl % {
                                      'page': 'Error %s ' % code,
                                      'title': responseCode[0],
                                      'message': responseCode[1]
                                  })

    def WriteResponseJSONError(self, code, obj=None):
        return self.WriteResponse(code,
                                  None,
                                  "application/json",
                                  "UTF-8",
                                  dumps(obj if type(obj) == dict else {}))

    def WriteResponseNotFound(self):
        if self._client._uWebServer._notFoundUrl:
            self.WriteResponseRedirect(self._client._uWebServer._notFoundUrl)
        else:
            return self.WriteResponseError(404)

    _msgTmpl = """\
    <html>
        <head>
            <title>%(page)s</title>
        </head>
        <body>
            <h1>%(title)s</h1>
            %(message)s
        </body>
    </html>
    """

    _responseCodes = {
        304: ('Not Modified', 'Document has not changed since given time'),
        400: ('Bad Request', 'Bad request syntax or unsupported method'),
        403: ('Forbidden', 'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented', 'Server does not support this operation')
    }

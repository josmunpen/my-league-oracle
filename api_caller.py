
class ApiCaller():

    def __init__(self, http_conn, headers):
        self._http_conn = http_conn
        self._headers = headers

    @property
    def http_conn(self):
        return self._http_conn

    @property
    def headers(self):
        return self._headers

    
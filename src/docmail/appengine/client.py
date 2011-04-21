"""
Overrides some stuff in suds to make it work with App Engine
"""

from google.appengine.api import memcache, urlfetch
from suds import cache, client, transport
from suds.client import Factory, ServiceSelector
from suds.options import Options
from suds.plugin import PluginContainer
from suds.reader import DefinitionsReader
from suds.servicedefinition import ServiceDefinition
from suds.transport.https import HttpAuthenticated
from suds.wsdl import Definitions
import docmail.client

# 1. override the u2open method so that we do not call socket.setdefaulttimeout() (which is blocked on app engine)

def u2open_appengine(self, u2request):
    
    tm = self.options.timeout
    url = self.u2opener()
    if self.u2ver() < 2.6:
        # socket.setdefaulttimeout(tm) can't call this on app engine
        return url.open(u2request)
    else:
        return url.open(u2request, timeout=tm)

transport.http.HttpTransport.u2open = u2open_appengine

# 2. override the default urlfetch.fetch() params so that the default timeout is 10 rather than 5 (10 is the max on app engine)

#old_fetch = urlfetch.fetch
#def new_fetch(url, payload=None, method=urlfetch.GET, headers={},
#              allow_truncated=False, follow_redirects=True,
#              deadline=10.0, validate_certificate=None):
#    return old_fetch(url, payload, method, headers,
#                     allow_truncated, follow_redirects,
#                     deadline, validate_certificate)
#urlfetch.fetch = new_fetch

# 3. override cache.Cache to use memcache for caching purposes
class MemCache(cache.Cache):
    def __init__(self, duration=3600):
        self.duration = duration
        self.client = memcache.Client()
    
    def get(self, id):
        return self.client.get(str(id))

    def getf(self, id):
        return self.get(id)
    
    def put(self, id, object):
        self.client.set(str(id), object, self.duration)
    
    def putf(self, id, fp):
        self.put(id, fp)
    
    def purge(self, id):
        self.client.delete(str(id))
    
    def clear(self):
        self.client.flush_all()
        
# 4. override the client.Client __init__() method to use the memcache implementation declared above
class Client(docmail.client.Client):
    def __init__(self, username, password, source='', wsdl_url=None, **kwargs):
        if not wsdl_url:
            wsdl_url = docmail.client.DOCMAIL_WSDL
        self.source = source
        self.username = username
        self.password = password
        
        self.return_format = 'XML'           
        self.failure_return_format = 'XML'


        options = Options()
        options.transport = HttpAuthenticated()
        self.options = options
        options.cache = MemCache()
        self.set_options(**kwargs)
        reader = DefinitionsReader(options, Definitions)
        self.wsdl = reader.open(wsdl_url)
        plugins = PluginContainer(options.plugins)
        plugins.init.initialized(wsdl=self.wsdl)
        self.factory = Factory(self.wsdl)
        self.service = ServiceSelector(self, self.wsdl.services)
        self.sd = []
        for s in self.wsdl.services:
            sd = ServiceDefinition(self.wsdl, s)
            self.sd.append(sd)
        self.messages = dict(tx=None, rx=None)
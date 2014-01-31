import cgi
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

import datetime



class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty()
    description = ndb.TextProperty()
    impact = ndb.TextProperty()
    documentation = ndb.TextProperty()
    rationale  = ndb.TextProperty()
    implementation_steps = ndb.TextProperty()    
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    technician = ndb.UserProperty()
    priority = ndb.StringProperty(choices=set(["sensitive", "routine"]))



DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

def encodeChangeRequest(cr):
    obj = {
        'summary': cr.summary, 
        'priority': cr.priority,
        'id': cr.key.urlsafe()
        }
    return obj

class CRListHandler(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        crs_query = ChangeRequest.query(
            ancestor=guestbook_key(guestbook_name)).order(-ChangeRequest.created_on)
        crs = crs_query.fetch(100)

        
        #crs = [ChangeRequest(summary='sample summary',priority='routine')]
        
        objs = []
        self.response.headers['Content-Type'] = 'application/json'   
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
            
        self.response.write(json.dumps({'changerequests': objs}))
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest(parent=guestbook_key(),
                           summary=form['summary'],priority=form['priority'])
        cr.put()
        self.response.write(json.dumps({'id': cr.key.urlsafe()}))
        
class CRHandler(webapp2.RequestHandler):
    def get(self, id):
        key = ndb.Key(urlsafe=id)
        cr = key.get()
        self.response.write(json.dumps({'changerequest': encodeChangeRequest(cr)}))
    def delete(self, id):
        key = ndb.Key(urlsafe=id)
        key.delete()
    


application = webapp2.WSGIApplication([
        webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
        webapp2.Route('/changerequests/<id:.*>', handler=CRHandler)
], debug=True)

import cgi
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import logging
import datetime


properties = [	'summary',
		'description',
		'impact',
		'documentation',
		'rationale',
		'implementation_steps',
		#'technician',
		'priority']
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
    audit_trail = ndb.JsonProperty()



DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)

class JSONEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self,obj)

def encodeChangeRequest(cr):
    obj = {
        'summary': cr.summary,
	'description': cr.description,
	'impact': cr.impact,
	'documentation': cr.documentation,
	'rationale': cr.rationale,
	'implementation_steps': cr.implementation_steps,
	'technician': str(cr.technician),
	'priority': cr.priority,
        'id': cr.key.urlsafe(),
        'audit_trail': cr.audit_trail
        }
    return obj



class CRListHandler(webapp2.RequestHandler):
    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        crs_query = ChangeRequest.query(
            ancestor=guestbook_key(guestbook_name)).order(-ChangeRequest.created_on)
        crs = crs_query.fetch(100)

        objs = []
        self.response.headers['Content-Type'] = 'application/json'   
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
            
        self.response.write(json.dumps({'changerequests': objs},cls=JSONEncoder))
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest(parent=guestbook_key())
        for k in (set(form.keys()) - set(['id'])):
            setattr(cr,k,form[k])
        cr.audit_trail = []
        cr.technician = users.get_current_user()
        cr.put()
        self.response.write(json.dumps({'id': cr.key.urlsafe(),
                                        'blah': cr.__repr__()},cls=JSONEncoder))
        
class CRHandler(webapp2.RequestHandler):
    def get(self, id):
        key = ndb.Key(urlsafe=id)
        cr = key.get()
        self.response.write(json.dumps({'changerequest': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        key = ndb.Key(urlsafe=id)
        cr = key.get()

        audit_entry = dict()
        audit_entry['date'] = datetime.datetime.now().isoformat()
        audit_entry['user'] = users.get_current_user().nickname()
        audit_entry['changes'] = []
        
        
        for p in properties:
            if getattr(cr,p) != form[p]:
                change = dict()
                change['property'] = p
                change['from'] = getattr(cr,p)
                change['to'] = form[p]
                audit_entry['changes'].append(change)
                setattr(cr,p,form[p])

        if len(audit_entry['changes']) != 0:
            cr.audit_trail.append(audit_entry)
            cr.put()
        self.response.write(json.dumps({'blah': cr.audit_trail.__repr__()},cls=JSONEncoder))
                
    def delete(self, id):
        key = ndb.Key(urlsafe=id)
        key.delete()
    
class LoginHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(json.dumps({'url': users.create_login_url(self.request.uri)}))


application = webapp2.WSGIApplication([
        webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
        webapp2.Route('/changerequests/<id:.*>', handler=CRHandler),
        webapp2.Route('/Login', handler=LoginHandler)
], debug=True)

logging.info(users.create_login_url("/"))

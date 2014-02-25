import cgi
import urllib
import json
import string

from google.appengine.api import users
from google.appengine.ext import ndb
from datamodel import ChangeRequest

import webapp2
import logging
import datetime

#directly editable properties
properties = {	'summary',
		'description',
		'impact',
		'documentation',
		'rationale',
		'implementation_steps',
		'technician',
		'priority',
		'tests_conducted',
		'risks',
		'backout_plan',
		'communication_plan',
		'layman_description',
                'startTime',
                'endTime'}




class JSONEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(obj)

def encodeChangeRequest(cr):
    obj = {
        'summary': cr.summary,
	'description': cr.description,
	'impact': cr.impact,
	'documentation': cr.documentation,
	'rationale': cr.rationale,
	'implementation_steps': cr.implementation_steps,
	'technician': cr.technician,
	'priority': cr.priority,
        'id': cr.key.id(),
	'created_on': cr.created_on,
        'audit_trail': cr.audit_trail,
	'tests_conducted': cr.tests_conducted,
	'risks': cr.risks,
	'backout_plan': cr.backout_plan,
	'communication_plan': cr.communication_plan,
	'layman_description': cr.layman_description,
        'startTime': cr.startTime,
        'endTime': cr.endTime
	}
    return obj



class CRListHandler(webapp2.RequestHandler):
    def get(self):
        logging.debug(self.request.params)
        crs_query = ChangeRequest.query().filter(ChangeRequest.status.IN(['created', 'approved'])) 
        params = self.request.params
        for field in set(params.keys()) & properties:
            crs_query = crs_query.filter(getattr(ChangeRequest,field) == params[field])
        crs = crs_query.order(-ChangeRequest.created_on).fetch(int(params['limit']), offset=int(params['offset']))

        objs = []
        self.response.headers['Content-Type'] = 'application/json'   
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
            
        logging.info(self.response.body)
        self.response.write(json.dumps({'changerequests': objs},cls=JSONEncoder))
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest()
        for k in (set(form.keys()) & properties):
            setattr(cr,k,form[k])
        cr.audit_trail = []
        cr.status = 'created'
        cr.author = users.get_current_user()
        cr.put()
        logging.debug(cr.key.id())
        self.response.write(json.dumps({'id': cr.key.id(),
                                        'blah': cr.__repr__()},cls=JSONEncoder))
        
class CRHandler(webapp2.RequestHandler):
    def get(self, id):
        cr = ChangeRequest.get_by_id(int(id))
        self.response.write(json.dumps({'changerequest': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        key = ndb.Key('ChangeRequest',int(id))
        cr = key.get()

        audit_entry = dict()
        audit_entry['date'] = datetime.datetime.now().isoformat()
        audit_entry['user'] = users.get_current_user().email()
        audit_entry['changes'] = []
        
        
        for p in properties:
            if (form[p] and str(getattr(cr,p)) != form[p] and
                p not in ['startTime', 'endTime']):
                change = dict()
                change['property'] = p
                change['from'] = str(getattr(cr,p))
                change['to'] = form[p]
                audit_entry['changes'].append(change)
                setattr(cr,p,form[p])

        if len(audit_entry['changes']) != 0:
            cr.audit_trail.append(audit_entry)
            cr.put()
        self.response.write(json.dumps({'blah': cr.audit_trail.__repr__()},cls=JSONEncoder))
                
    def delete(self, id):
        key = ndb.Key('ChangeRequest',int(id))
        key.delete()
class DraftListHandler(webapp2.RequestHandler):
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest()
        cr.audit_trail = []
        cr.status = 'draft'
        cr.author = users.get_current_user()
        for p in (set(form.keys()) & properties):
            if form[p] and str(getattr(cr,p)) != form[p]:
                setattr(cr,p,form[p])
        cr.put()
        self.response.write(json.dumps({'id': cr.key.id()}))
    def get(self):
        crs_query = ChangeRequest.query().filter(ChangeRequest.status == 'draft', ChangeRequest.author == users.get_current_user())
        crs = crs_query.order(-ChangeRequest.created_on).fetch(100)
        objs = []
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
        self.response.write(json.dumps({'drafts': objs},cls=JSONEncoder)) 
    
class DraftHandler(webapp2.RequestHandler):
    def get(self, id):
        cr = ChangeRequest.get_by_id(int(id))
        self.response.write(json.dumps({'draft': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        changed = False
        cr = ChangeRequest.get_by_id(int(id))
        if cr.status == 'draft' and cr.author == users.get_current_user():
            for p in (set(form.keys()) & properties):
                if form[p] and str(getattr(cr,p)) != form[p]:
                    setattr(cr,p,form[p])
                    changed = True
        if changed:
            cr.put()
    def delete(self, id):
        cr = ChangeRequest.get_by_id(int(id))
        if cr.status == 'draft' and cr.author == users.get_current_user():
            cr.delete()
class UserHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(json.dumps({'user': users.get_current_user().email()}))
       
        
        
    
application = webapp2.WSGIApplication([
        webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
        webapp2.Route('/changerequests/<id:.*>', handler=CRHandler),
        webapp2.Route('/Logout',webapp2.RedirectHandler, defaults={'_uri': users.create_logout_url('/')}),
        webapp2.Route('/user',handler=UserHandler),
        webapp2.Route('/drafts',handler=DraftListHandler),
        webapp2.Route('/drafts/<id:.*>',handler=DraftHandler)

], debug=True)

import cgi
import urllib
import json

from google.appengine.api import users
from google.appengine.ext import ndb
from datamodel import ChangeRequest
from dateutil.parser import *

import webapp2
import logging
import datetime

properties = [	'summary',
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
                'endTime']


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
	'technician': cr.technician,
	'priority': cr.priority,
        'id': cr.key.urlsafe(),
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
        logging.info(self.request.params)
        crs_query = ChangeRequest.query()
        for field in self.request.params:
            crs_query = crs_query.filter(getattr(ChangeRequest,field) == self.request.params[field])
        crs = crs_query.order(-ChangeRequest.created_on).fetch(100)

        objs = []
        self.response.headers['Content-Type'] = 'application/json'   
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
            
        logging.info(self.response.body)
        self.response.write(json.dumps({'changerequests': objs},cls=JSONEncoder))
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest()
        for k in (set(form.keys()) & set(properties)):
            if k == 'startTime' or k == 'endTime':
                setattr(cr,k,dateutil.parser.parse(form[k]))
            setattr(cr,k,form[k])
        cr.audit_trail = []
        cr.author = users.get_current_user()
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
        audit_entry['user'] = users.get_current_user().email()
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
class UserHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(json.dumps({'user': users.get_current_user().email()}))
    
application = webapp2.WSGIApplication([
        webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
        webapp2.Route('/changerequests/<id:.*>', handler=CRHandler),
        webapp2.Route('/Logout',webapp2.RedirectHandler, defaults={'_uri': users.create_logout_url('/')}),
        webapp2.Route('/user',handler=UserHandler)
], debug=True)

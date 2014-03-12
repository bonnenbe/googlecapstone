import cgi
import urllib
import json
import string

from google.appengine.api import users
from google.appengine.ext import ndb
from datamodel import *

import webapp2
import logging
import datetime


class JSONEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.isoformat() + 'Z'
        elif isinstance(obj,users.User):
	    return obj.email()
        return json.JSONEncoder.default(self,obj)

def intersperse(iterable, delimiter):
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x
def IDsToKey(IDstring):
    IDs = string.split(IDstring, '-')
    pairs = []
    for id in IDs:
        pairs.append(('ChangeRequest', int(id)))
    return ndb.Key(pairs=pairs)

    
def encodeChangeRequest(cr):
    obj = {
        'summary': cr.summary,
        'description': cr.description,
        'impact': cr.impact,
        'documentation': cr.documentation,
        'rationale': cr.rationale,
        'implementation_steps': cr.implementation_steps,
        'technician': cr.technician,
	'peer_reviewer': cr.peer_reviewer,
        'priority': cr.priority,
        'id': string.join(intersperse(map(lambda x: str(x[1]), cr.key.pairs()), '-')),
        'created_on': cr.created_on,
        'audit_trail': cr.audit_trail,
        'tests_conducted': cr.tests_conducted,
        'risks': cr.risks,
        'backout_plan': cr.backout_plan,
        'communication_plan': cr.communication_plan,
        'layman_description': cr.layman_description,
        'startTime': cr.startTime,
        'endTime': cr.endTime,
	'status': cr.status,
	'tags': cr.tags
	}
    return obj

#returns true if property p and string s are equivalent
def equals(p,s):
    if isinstance(s, list):
        return set(p) == set(s)
    elif isinstance(p,datetime.datetime):
        return p == stringtodatetime(s)
    elif isinstance(p,users.User):
        return p.email() == s
    else:
        return str(p) == str(s)

class BaseHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        # Log the error.
        logging.exception(exception)

        # Set a custom message.
        self.response.write('An error occurred.')

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)

class CRListHandler(BaseHandler):
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
        logging.info(form['tags'])
        logging.info(cr.tags)
        cr.put()
        logging.debug(cr.key.id())
        self.response.write(json.dumps({'id': cr.key.id(),
                                        'blah': cr.__repr__()},cls=JSONEncoder))
                                        
        try:
            index = search.Index(name="fullTextSearch")
            index.put(cr.toSearchDocument())
        except search.Error:
            logging.exception("Put failed")
            
class CRHandler(BaseHandler):
    def get(self, id):
        key = IDsToKey(id)
        cr = key.get()
        self.response.write(json.dumps({'changerequest': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        key = IDsToKey(id)
        cr = key.get()

            

        audit_entry = dict()
        audit_entry['date'] = datetime.datetime.now().isoformat()
        audit_entry['user'] = users.get_current_user().email()
        audit_entry['changes'] = []
        
        
        for p in (set(form.keys()) & properties):
	    if not equals(getattr(cr,p), form[p]):
                change = dict()
                change['property'] = p
                change['from'] = str(getattr(cr,p))
                setattr(cr,p,form[p])
                change['to'] = str(getattr(cr,p))
                audit_entry['changes'].append(change)

        if len(audit_entry['changes']) != 0:
            cr.audit_trail.insert(0, audit_entry)
            cr.put()
        self.response.write(json.dumps({'blah': cr.audit_trail.__repr__()},cls=JSONEncoder))
                
    def delete(self, id):
        IDsToKey(id).delete()

class DraftListHandler(BaseHandler):
    def post(self):
        form = json.loads(self.request.body)
        if 'id' in form.keys() and form['id']:
            key = IDsToKey(form['id'])
            parentCR = key.get()
            if parentCR.status in ['created', 'approved']:
                cr = ChangeRequest(parent=key)
            else:
                cr = ChangeRequest()
        else:
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
        params = self.request.params
        for field in set(params.keys()) & properties:
            crs_query = crs_query.filter(getattr(ChangeRequest,field) == params[field])
        crs = crs_query.order(-ChangeRequest.created_on).fetch(int(params['limit']), offset=int(params['offset']))
        objs = []
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
        self.response.write(json.dumps({'drafts': objs},cls=JSONEncoder)) 
    def delete(self):
        crs_query = ChangeRequest.query().filter(ChangeRequest.status == 'draft', ChangeRequest.author == users.get_current_user())
        crs = crs_query.fetch(keys_only=True)
        ndb.delete_multi(crs)
        
class DraftHandler(BaseHandler):
    def get(self, id):
        key = IDsToKey(id)
        cr = key.get()
        self.response.write(json.dumps({'changerequest': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        changed = False
        cr = IDsToKey(id).get()
        if cr.status == 'draft' and cr.author == users.get_current_user():
            for p in (set(form.keys()) & properties):
                if not equals(getattr(cr,p), form[p]):
                    setattr(cr,p,form[p])
                    changed = True
        if changed:
            cr.put()
    def delete(self, id):
        cr = IDsToKey(id).get()
        if cr.status == 'draft' and cr.author == users.get_current_user():
            cr.key.delete()
class UserHandler(BaseHandler):
    def get(self):
        self.response.write(json.dumps({'user': users.get_current_user().email()}))
       
class ApprovalHandler(BaseHandler):
    def put(self, id):
	group_query = UserGroup.query().filter( UserGroup.members == users.get_current_user(), UserGroup.name == 'admins')
	key = IDsToKey(id)
        cr = key.get()
	if (group_query.count(limit=1) and cr.priority == 'sensitive') or cr.priority != 'sensitive':
	    form = json.loads(self.request.body)
	    form['status'] = 'approved'

            audit_entry = dict()
            audit_entry['date'] = datetime.datetime.now().isoformat()
            audit_entry['user'] = users.get_current_user().email()
            audit_entry['changes'] = []
        
        
            if (form['status'] and str(getattr(cr,'status')) != form['status']):
            	change = dict()
	    	change['property'] = 'status'
            	change['from'] = str(getattr(cr,'status'))
            	change['to'] = form['status']
            	audit_entry['changes'].append(change)
            	setattr(cr,'status',form['status'])

            if len(audit_entry['changes']) != 0:
                cr.audit_trail.append(audit_entry)
                cr.put()
            self.response.write(json.dumps({'blah': cr.audit_trail.__repr__()},cls=JSONEncoder))
	else :
	    webapp2.abort(403)

class GroupHandler(BaseHandler):
	def post(self):
        	form = json.loads(self.request.body)
        	group = UserGroup()
        	for k in (set(form.keys())):
			if k != 'name':
				UserList = []
				for s in form[k].split(','):
					newUser = users.User(email=s)
					UserList.append(newUser)
				setattr(group,k,UserList)
			else: 
				setattr(group,k,form[k])
        	group.put()
        	logging.debug(group.key.id())
        	self.response.write(json.dumps({'id': group.key.id()},cls=JSONEncoder))

		
        
    
application = webapp2.WSGIApplication([
        webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
        webapp2.Route('/changerequests/<id:.*>', handler=CRHandler),
        webapp2.Route('/Logout',webapp2.RedirectHandler, defaults={'_uri': users.create_logout_url('/')}),
        webapp2.Route('/user',handler=UserHandler),
        webapp2.Route('/drafts',handler=DraftListHandler),
        webapp2.Route('/drafts/<id:.*>',handler=DraftHandler),
	webapp2.Route('/approve/<id:.*>', handler = ApprovalHandler),
	webapp2.Route('/usergroups', handler = GroupHandler)

], debug=True)

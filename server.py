import cgi
import urllib
import json
import string

from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import ndb
from google.appengine.ext import search
from datamodel import *


import webapp2
import logging
import datetime

appEmail = "notifications@chromatic-tree-459.appspotmail.com"
destinationEmail = "bbonnen@gmail.com"

class JSONEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.isoformat() + 'Z'
        elif isinstance(obj,users.User):
            return obj.email()
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
        'peer_reviewer': cr.peer_reviewer,
        'priority': cr.priority,
        'id': keyToIDs(cr.key),
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
        'tags': cr.tags,
        'cc_list': [user.email() for user in cr.cc_list]
    }
    return obj

#returns true if property p and string s are equivalent
def equals(p,s):
    if isinstance(s, list):
        if len(p) > 0 and isinstance(p[0], users.User):
            return {user.email() for user in p} == set(s)
        else:
            return set(p) == set(s)
    elif isinstance(p,datetime.datetime):
        return p == stringtodatetime(s)
    elif isinstance(p,users.User):
        return p.email() == s
    else:
        return str(p) == str(s)
@ndb.non_transactional
def updateIndex(entity, indexName):
    index = search.Index(name=indexName)
    index.put(entity.toSearchDocument())
@ndb.non_transactional
def removeFromIndex(id, indexName):
    index = search.Index(name=indexName)
    index.delete([id])
@ndb.transactional
def _addTag(tagstring):
    tag = Tag.get_or_insert(tagstring)
    tag.frequency += 1
    tag.put()
    updateIndex(tag, "tags")
@ndb.transactional
def _removeTag(tagstring):
    tag = Tag.get_or_insert(tagstring)
    tag.frequency -= 1
    if tag.frequency <= 0:
        tag.key.delete()
    else:
        tag.put()
    removeFromIndex(tag.key.id(), "tags")
def updateTags(added, removed):
    for tag in added:
        _addTag(tag)
    for tag in removed:
        _removeTag(tag)


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


        # full text search stuff
        if 'query' in params and params['query']:
                             
            index = search.Index(name="fullTextSearch")
            
            query_string = urllib.unquote(params['query'])
            
            sort_opts = search.SortOptions()
            # sort options
            logging.debug(params['sort'])
            if 'sort' in params and params['sort']:
                direction = search.SortExpression.DESCENDING
                if direction in params and params['direction'] == 'ascending':
                    direction = search.sortExpression.ASCENDING
                    
                sort1 = search.SortExpression(expression=params['sort'], direction=direction, default_value=0)
                sort_opts = search.SortOptions(expressions = [sort1])
            
            options = search.QueryOptions(
                limit = int(params['limit']) if 'limit' in params else 10,
                offset = int(params['offset']) if 'offset' in params else 0,
                ids_only = True,
                sort_options = sort_opts
            )
            
            query = search.Query(options=options, query_string=query_string)
            
            try:
                # list comprehension
                results = index.search(query).results
                #logging.debug(results)
                #doc_ids = [document.doc_id for document in index.search(query_string)]
                
                keys = [ndb.Key(urlsafe=doc.doc_id) for doc in results]
                crs = ndb.get_multi(keys)
            except search.Error:
                logging.exception('Search failed')
            
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
        mail_list = {user.email() for user in {cr.author, cr.technician} | set(cr.cc_list) if user}
        if mail_list:
            mail.send_mail( sender = appEmail, 
                            to = mail_list,
                            subject= "CR #" + str(cr.key.id()) + " has been created",
                            body = "Change request id " + str(cr.key.id()) + " has been created. \n\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/#/id=" + str(cr.key.id()) + "\n\n Thanks, \nChange Management Team")
        mail_list = {user.email() for user in {cr.peer_reviewer} if user}
        if mail_list:    
            mail.send_mail( sender = appEmail,
                            to = mail_list,
                            subject= "CR #" + str(cr.key.id()) + " needs your approval",
                            body = "Change request id " + str(cr.key.id()) + " needs your approval.\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/#/id=" + str(cr.key.id()) + "\n\nThanks, \nChange Management Team")
        logging.debug(cr.key.id())
        self.response.write(json.dumps({'id': keyToIDs(cr.key),
                                        'blah': cr.__repr__()},cls=JSONEncoder))
        
        updateTags(cr.tags, [])

        # add to search api full text search
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
        updated, approved, commented = False, False, False
        if cr.status not in ['created', 'approved', 'succeeded', 'failed']:
            webapp2.abort(403) #wrong uri

        audit_entry = dict()
        audit_entry['date'] = datetime.datetime.now().isoformat()
        audit_entry['user'] = users.get_current_user().email()
        audit_entry['changes'] = []
        if 'comment' in form.keys() and form['comment']:
            audit_entry['comment'] = form['comment']
            commented = True
        
        if 'priority' in form.keys() and form['priority'] == 'sensitive' and cr.priority == 'routine' and cr.status != 'created':
            #reset status if making CR sensitive            
            audit_entry['changes'].append({'property': 'status',
                                           'from': cr.status,
                                           'to': 'created'})
            cr.status = 'created'
            form.pop('status', None)
            change = dict()
            change['property'] = 'priority'
            change['from'] = 'routine'
            change['to'] = 'sensitive'
            cr.priority = 'sensitive'
            form.pop('priority', None)
            audit_entry['changes'].append(change)
            updated = True
        if 'status' in form.keys() and form['status'] == 'approved' and cr.status == 'created':
            #attempting to approve
            committee = UserGroup.get_or_insert('approvalcommittee').members        
            if cr.priority != 'sensitive' or (users.get_current_user() in committee and cr.priority == 'sensitive'):
                cr.status = 'approved'
                cr.approved_on = datetime.datetime.now()
                change = dict()
                change['property'] = 'status'
                change['from'] = 'created'
                change['to'] = 'approved'
                audit_entry['changes'].append(change)
                form.pop('status', None)
                updated = True
                approved = True
            else:
                webapp2.abort(403) #forbidden approval
        if 'status' in form.keys() and (form['status'] == 'failed' or form['status'] == 'succeeded'):
                change = dict()
                change['property'] = 'status'
                change['from'] = cr.status
                change['to'] = form['status']
                cr.status = form['status']
                form.pop('status', None)
                audit_entry['changes'].append(change)
                updated = True

        if 'tags' in form.keys():
            updateTags(set(form['tags']) - set(cr.tags),
                       set(cr.tags) - set(form['tags']))
        for p in (set(form.keys()) & properties):
            if not equals(getattr(cr,p), form[p]):
                change = dict()
                change['property'] = p
                change['from'] = str(getattr(cr,p))
                setattr(cr,p,form[p])
                change['to'] = str(getattr(cr,p))
                audit_entry['changes'].append(change)
                updated = True

        if updated or commented:
            cr.audit_trail.insert(0, audit_entry)
            cr.put()
            mail_list = {user.email() for user in {cr.author, cr.peer_reviewer, cr.technician} | set(cr.cc_list) if user}

            if mail_list:
                #TODO tailor email for commented but not updated
                if approved:
                    mail.send_mail( sender = appEmail, 
                                    to = mail_list,
                                    subject= "CR #" + str(cr.key.id()) + " has been approved",
                                    body = "CR #" + str(cr.key.id()) + " has been approved." + "\n\n View here: http://www.chromatic-tree-459.appspot.com/#/id=" + str(cr.key.id()) + "\n\nThanks, \nChange Management Team")
                else:
                    mail.send_mail( sender = appEmail, 
                                    to = mail_list,
                                    subject= "CR #" + str(cr.key.id()) + " has been edited",
                                    body = "Change request id " + str(cr.key.id()) + " has been edited by " + str(audit_entry["user"]) +".\n\n View here: http://www.chromatic-tree-459.appspot.com/#/id=" + str(cr.key.id()))

            
            # update document in full text search api
            try:
                index = search.Index(name="fullTextSearch")
                index.put(cr.toSearchDocument())
            except search.Error:
                logging.exception("Put failed")
    def delete(self, id):
        key = IDsToKey(id)
        updateTags([], key.get().tags)
        try:
            index = search.Index(name="fullTextSearch")
            index.delete([key.urlsafe()])
        except search.Error:
            logging.exception("Put failed")
        key.delete()

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
            setattr(cr,p,form[p])
        cr.put()
        logging.info("KEY ID:" + keyToIDs(cr.key))
        self.response.write(json.dumps({'id': keyToIDs(cr.key)}))
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
class TemplateListHandler(BaseHandler):
    def post(self):
        form = json.loads(self.request.body)
        cr = ChangeRequest()
        cr.audit_trail = []
        cr.status = 'template'
        cr.author = users.get_current_user()
        for p in (set(form.keys()) & properties):
            setattr(cr,p,form[p])
        cr.put()
        self.response.write(json.dumps({'id': keyToIDs(cr.key)}))
    def get(self):
        crs_query = ChangeRequest.query().filter(ChangeRequest.status == 'template')
        params = self.request.params
        for field in set(params.keys()) & properties:
            crs_query = crs_query.filter(getattr(ChangeRequest,field) == params[field])
        crs = crs_query.order(-ChangeRequest.created_on).fetch(int(params['limit']) if 'limit' in params else 10,
                                                               offset=int(params['offset']) if 'offset' in params else 0)
        objs = []
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
        self.response.write(json.dumps({'templates': objs},cls=JSONEncoder)) 
        
class TemplateHandler(BaseHandler):
    def get(self, id):
        key = IDsToKey(id)
        cr = key.get()
        self.response.write(json.dumps({'template': encodeChangeRequest(cr)},cls=JSONEncoder))
    def put(self, id):
        form = json.loads(self.request.body)
        changed = False
        cr = IDsToKey(id).get()
        if cr.status == 'template' and cr.author == users.get_current_user():
            for p in (set(form.keys()) & properties):
                if not equals(getattr(cr,p), form[p]):
                    setattr(cr,p,form[p])
                    changed = True
        if changed:
            cr.put()
    def delete(self, id):
        cr = IDsToKey(id).get()
        if cr.status == 'template' and cr.author == users.get_current_user():
            cr.key.delete()
class UserHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        admins = UserGroup.get_or_insert('admins')
        committee = UserGroup.get_or_insert('approvalcommittee')
        inAdmins = user in admins.members
        inCommittee = user in committee.members
        self.response.write(json.dumps({'user': user.email(),
                                        'inAdmins' : inAdmins,
                                        'inCommittee' : inCommittee}))
       
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

            

class IndexHandler(BaseHandler):
    def get(self):
    
        # force update on search index via /admin/rebuildIndex
        crs_query = ChangeRequest.query().filter(ChangeRequest.status.IN(['created', 'approved']))
        
        for cr in crs_query:
            index = search.Index(name="fullTextSearch")
            index.put(cr.toSearchDocument())
class TempHandler(BaseHandler):
    def get(self):
        admins = UserGroup.get_or_insert('admins')
        committee = UserGroup.get_or_insert('approvalcommittee')
        coolpeople = {users.User(email) for email in {"vogtnich@gmail.com", "guoalber1@gmail.com", "bbonnen@gmail.com",
                                                  "antarus@google.com", "krelinga@google.com", "bgilmore@google.com"}}
        for person in coolpeople:
            if person not in admins.members:
                admins.members.append(person)
                admins.name = "admins"
                admins.put()
            if person not in committee.members:
                committee.members.append(person)
                admins.name = "Approval Committee"
                committee.put()

    
        
            
class TagsHandler(BaseHandler):
    def get(self):
        params = self.request.params
        index = search.Index(name="tags")
        options = search.QueryOptions(
            limit = int(params['limit']) if 'limit' in params else 10,
            offset = int(params['offset']) if 'offset' in params else 0,
            ids_only = True
        )
        query = search.Query(options=options,
                             query_string="text:" + params['query'] if 'query' in params else "")
        try:
            results = index.search(query).results
        except search.Error:
            webapp2.abort(400)
        self.response.write(json.dumps([doc.doc_id for doc in results],cls=JSONEncoder))
            
class SearchHandler(BaseHandler):
    def get(self):
        pass

            
application = webapp2.WSGIApplication([
    webapp2.Route('/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
    webapp2.Route('/changerequests/<id:.*>', handler=CRHandler),
    webapp2.Route('/Logout',webapp2.RedirectHandler, defaults={'_uri': users.create_logout_url('/')}),
    webapp2.Route('/user',handler=UserHandler),
    webapp2.Route('/drafts',handler=DraftListHandler),
    webapp2.Route('/drafts/<id:.*>',handler=DraftHandler),
    webapp2.Route('/templates',handler=TemplateListHandler),
    webapp2.Route('/templates/<id:.*>',handler=TemplateHandler),
    webapp2.Route('/tags', handler = TagsHandler),
    webapp2.Route('/usergroups', handler = GroupHandler),
    webapp2.Route('/admin/rebuildIndex', handler = IndexHandler),
    webapp2.Route('/admin/temp', handler = TempHandler), 
    webapp2.Route('/search', handler = SearchHandler)

], debug=True)

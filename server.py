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

def customizeJSON():
    original = json.JSONEncoder.default
    def default(self,obj):
        if isinstance(obj,datetime.datetime):
            return obj.isoformat() + 'Z'
        elif isinstance(obj,users.User):
            return obj.email()
        return original(self,obj)

    json.JSONEncoder.default = default
customizeJSON()

    
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
        'id': cr.id(),
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
    try:
        index = search.Index(name=indexName)
        index.put(entity.toSearchDocument())
    except search.Error:
        logging.exception("Put failed")
@ndb.non_transactional
def removeFromIndex(id, indexName):
    try:
        index = search.Index(name=indexName)
        index.delete([id])
    except search.Error:
        logging.exception("Delete failed")
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

def getMailList(cr):
    nonapprovers, approvers = set(), set()
    if cr.author and Preferences.get_or_insert(cr.author.email()).notifyAuthor:
        nonapprovers.add(cr.author.email())
    if cr.technician and Preferences.get_or_insert(cr.technician.email()).notifyTechnician:
        nonapprovers.add(cr.technician.email())
    if cr.peer_reviewer and Preferences.get_or_insert(cr.peer_reviewer.email()).notifyReviewer:
        approvers.add(cr.peer_reviewer.email())
    cc = {user.email() for user in cr.cc_list}
    if cr.priority == 'sensitive':
        committee = UserGroup.get_or_insert('approvalcommittee').members
        for member in committee:
            if Preferences.get_or_insert(member.email()).notifyCommittee:
                approvers.add(member.email())
    return nonapprovers - approvers, approvers, cc - nonapprovers - approvers

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
    def queryIndex(self, indexName, private=False):
        params = self.request.params
        index = search.Index(name=indexName)
        if 'query' in params:
            query_string = urllib.unquote(params['query'])
        else:
            query_string = ""
            
        if private:
            query_string = "technician:\"" + users.get_current_user().email() + '\" ' + query_string
        sort_opts = search.SortOptions()
            

        if 'sort' in params and params['sort']:
            expressions = []
            for (sort,direction) in map(None, params.getall('sort'), params.getall('direction')):
                if sort:
                    if direction == 'asc':
                        direction = search.SortExpression.ASCENDING
                    else:
                        direction = search.SortExpression.DESCENDING
                    attr = getattr(ChangeRequest, sort);
                    expressions.append(search.SortExpression(expression=sort, 
                                                             direction=direction, 
                                                             default_value=0 if isinstance(attr, ndb.DateTimeProperty) else ""))
            sort_opts = search.SortOptions(expressions=expressions)
        else:
            sort_opts = None
        options = search.QueryOptions(
            limit = int(params['limit']) if 'limit' in params else 10,
            offset = int(params['offset']) if 'offset' in params else 0,
            ids_only = True,
            sort_options = sort_opts
            )
            
        query = search.Query(options=options, query_string=query_string)
        results = index.search(query).results
        keys = [ndb.Key(urlsafe=doc.doc_id) for doc in results]
        crs = ndb.get_multi(keys)
        return crs
    def queryDatastore(self, statuses=None, private=False):
        logging.info('using datastore query')
        params = self.request.params
        crs_query = ChangeRequest.query()
        if statuses:
            crs_query = crs_query.filter(ChangeRequest.status.IN(statuses))
        if private:
            crs_query = crs_query.filter(ChangeRequest.author == users.get_current_user())
        if 'sort' in params and params['sort']:
            for (sort,direction) in map(None, params.getall('sort'), params.getall('direction')):
                if sort:
                    if direction and direction == 'asc':
                        crs_query = crs_query.order(getattr(ChangeRequest,sort))
                    else:
                        crs_query = crs_query.order(-getattr(ChangeRequest,sort))
        else:
            crs_query = crs_query.order(-ChangeRequest.created_on)
        crs = crs_query.fetch(int(params['limit']) if 'limit' in params else 10,
                              offset=int(params['offset']) if 'offset' in params else 0)
        return crs
    def isSimpleSort(self):
        params = self.request.params    
        return 'query' not in params or not params['query']
    def encodeCRList(self, crs):
        objs = []
        for cr in crs:
            objs.append(encodeChangeRequest(cr))
        return objs
    def getCR(self, id):
        cr = IDsToKey(id).get()
        if cr:
            return cr
        else:
            self.abort(404)
    def query(self,indexName,statuses=None,private=False):
        # if self.isSimpleSort():
        #     crs = self.queryDatastore(statuses=statuses,private=private)
        # else:
        crs = self.queryIndex(indexName=indexName,private=private)
        return crs


class CRListHandler(BaseHandler):
    def get(self):
        crs = self.query(indexName='fullTextSearch',statuses=['created','approved', 'succeeded', 'failed'])
        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(self.encodeCRList(crs)))
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
        nonapprovers, approvers, cc = getMailList(cr)
        for recipient in nonapprovers | cc:
            mail.send_mail(sender = appEmail,
                           to = recipient,
                           subject = "CR #" + cr.id() + " has been created",
                           body = "Change request id " + cr.id() + " has been created by " + str(cr.author) + "\n\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/id=" + cr.id() + "\n\n Thanks, \nChange Management Team")
        for recipient in approvers:
            mail.send_mail(sender = appEmail,
                           to = recipient,
                           subject= "CR #" + cr.id() + " needs your approval",
                           body = "Change request id " + cr.id() + " needs your approval. \n\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/id=" + cr.id() + "\n\n Thanks, \nChange Management Team")
        logging.debug(cr.key.id())
        self.response.write(json.dumps({'id': cr.id()}))
        updateTags(cr.tags, [])
        updateIndex(cr, 'fullTextSearch')
        
        
            
class CRHandler(BaseHandler):
    def get(self, id):
        cr = self.getCR(id)
        self.response.write(json.dumps(encodeChangeRequest(cr)))
    def put(self, id):
        form = json.loads(self.request.body)
        cr = self.getCR(id)
        updated, approved, commented, unapproved = False, False, False, False
        if cr.status not in ['created', 'approved', 'succeeded', 'failed']:
            webapp2.abort(403) #wrong uri

        audit_entry = dict()
        audit_entry['date'] = datetime.datetime.now()
        audit_entry['user'] = users.get_current_user()
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
        if 'status' in form.keys() and form['status'] == 'created' and cr.status == 'approved':
            committee = UserGroup.get_or_insert('approvalcommittee').members        
            if cr.priority != 'sensitive' or (users.get_current_user() in committee and cr.priority == 'sensitive'):
                cr.status = 'created'
                change = dict()
                change['property'] = 'status'
                change['from'] = 'approved'
                change['to'] = 'created'
                audit_entry['changes'].append(change)
                form.pop('status', None)
                updated = True
                unapproved = True
            else:
                webapp2.abort(403) #forbidden approval
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
        if 'status' in form.keys() and (form['status'] == 'failed' or form['status'] == 'succeeded'): #fix permissions
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
                change['from'] = getattr(cr,p)
                setattr(cr,p,form[p])
                change['to'] = getattr(cr,p)
                audit_entry['changes'].append(change)
                updated = True

        if updated or commented:
            cr.audit_trail.insert(0, audit_entry)
            cr.put()
            if approved:
                subject = "CR #" + cr.id() + " has been approved"
                body = "Change request id " + cr.id() + " has been approved by " + str(audit_entry["user"]) + "\n\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/id=" + cr.id() + "\n\n Thanks, \nChange Management Team"
            elif commented and not updated:
                subject = "CR #" + cr.id() + " has a new comment"
                body = "Change request id " + cr.id() + " has a new comment by " + str(audit_entry["user"]) + "\n\nSummary: \n" + str(cr.summary) + "\n\nComment: \n" + str(audit_entry['comment']) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/id=" + cr.id() + "\n\n Thanks, \nChange Management Team"
            else:
                subject = "CR #" + cr.id() + " has been edited"
                body = "Change request id " + cr.id() + " has been edited by " + str(audit_entry["user"]) + "\n\nSummary: \n" + str(cr.summary) + "\n\n View here: http://www.chromatic-tree-459.appspot.com/id=" + cr.id() + "\n\n Thanks, \nChange Management Team"
            nonapprovers, approvers, cc = getMailList(cr)
            for recipient in nonapprovers | approvers | cc:
                mail.send_mail(sender=appEmail, to=recipient, subject=subject, body=body)
            updateIndex(cr, 'fullTextSearch')
    def delete(self, id):
        key = IDsToKey(id)
        cr = key.get()
        if cr.author != users.get_current_user():
            self.abort(403)
        updateTags([], cr.tags)
        removeFromIndex(key.urlsafe(),"fullTextSearch")
        key.delete()

class DraftListHandler(BaseHandler):
    def post(self):
        form = json.loads(self.request.body)
        if 'id' in form.keys() and form['id']:
            key = IDsToKey(form['id'])
            parentCR = key.get()
            if parentCR.status not in ['draft', 'template']:
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
        updateIndex(cr, 'drafts')

        self.response.write(json.dumps({'id': cr.id()}))
    def get(self):
        crs = self.query(indexName='drafts',statuses=['draft'],private=True)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(self.encodeCRList(crs)))
    def delete(self):
        crs_query = ChangeRequest.query().filter(ChangeRequest.status == 'draft', ChangeRequest.author == users.get_current_user())
        keys = crs_query.fetch(keys_only=True)
        for id in [key.urlsafe() for key in keys]:
            removeFromIndex(id,'drafts')
        ndb.delete_multi(keys)
        
class DraftHandler(BaseHandler):
    def get(self, id):
        cr = self.getCR(id)
        self.response.write(json.dumps(encodeChangeRequest(cr)))
    def put(self, id):
        form = json.loads(self.request.body)
        changed = False
        cr = self.getCR(id)
        if cr.status == 'draft' and cr.author == users.get_current_user():
            for p in (set(form.keys()) & properties):
                if not equals(getattr(cr,p), form[p]):
                    setattr(cr,p,form[p])
                    changed = True
        if changed:
            cr.put()
            updateIndex(cr, 'drafts')
    def delete(self, id):
        cr = IDsToKey(id).get()
        if cr.status == 'draft' and cr.author == users.get_current_user():
            cr.key.delete()
            removeFromIndex(cr.key.urlsafe(),'drafts')
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
        updateIndex(cr, 'templates')
        self.response.write(json.dumps({'id': cr.id()}))
    def get(self):
        crs = self.query(indexName='templates',statuses=['template'])

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.dumps(self.encodeCRList(crs)))
        
class TemplateHandler(BaseHandler):
    def get(self, id):
        cr = self.getCR(id)
        self.response.write(json.dumps(encodeChangeRequest(cr)))
    def put(self, id):
        form = json.loads(self.request.body)
        changed = False
        cr = self.getCR(id)
        if cr.status == 'template' and cr.author == users.get_current_user():
            for p in (set(form.keys()) & properties):
                if not equals(getattr(cr,p), form[p]):
                    setattr(cr,p,form[p])
                    changed = True
        if changed:
            cr.put()
            updateIndex(cr, 'templates')
    def delete(self, id):
        cr = IDsToKey(id).get()
        if cr.status == 'template' and cr.author == users.get_current_user():
            cr.key.delete()
            removeFromIndex(cr.key.urlsafe(),'templates')
class UserHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        admins = UserGroup.get_or_insert('admins')
        committee = UserGroup.get_or_insert('approvalcommittee')
        preferences = Preferences.get_or_insert(user.email())
        inAdmins = user in admins.members
        inCommittee = user in committee.members
        self.response.write(json.dumps({'user': user.email(),
                                        'inAdmins' : inAdmins,
                                        'inCommittee' : inCommittee,
                                        'preferences' : preferences.toJSON()}))
    def put(self):
        user = users.get_current_user()
        preferences = Preferences.get_or_insert(user.email())
        form = json.loads(self.request.body)
        for k in form.keys():
            setattr(preferences,k,form[k])
        preferences.put()
    def delete(self):
        user = users.get_current_user()
        preferences = Preferences.get_or_insert(user.email())
        preferences.key.delete()
        
        
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
        self.response.write(json.dumps({'id': group.key.id()}))

            

class IndexHandler(BaseHandler):
    def get(self):
    
        # force update on search index via /admin/rebuildIndex
        crs_query = ChangeRequest.query().filter(ChangeRequest.status.IN(['created', 'approved', 'failed', 'succeeded']))
        
        
        #delete everything in the other indices
        doc_index = search.Index(name="drafts")
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)
        
        doc_index = search.Index(name="templates")
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)
        
        
        #delete everything in the index
        doc_index = search.Index(name="fullTextSearch")
        # looping because get_range by default returns up to 100 documents at a time
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id
                            for document in doc_index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            doc_index.delete(document_ids)
        
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
            if person not in committee.members:
                committee.members.append(person)
        admins.name = "admins"
        admins.put()
        committee.name = "Approval Committee"
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
        self.response.write(json.dumps([doc.doc_id for doc in results]))
            
            
application = webapp2.WSGIApplication([
    webapp2.Route('/api/changerequests', handler=CRListHandler, methods=['GET' ,'POST']),
    webapp2.Route('/api/changerequests/<id:.*>', handler=CRHandler),
    webapp2.Route('/api/Logout',webapp2.RedirectHandler, defaults={'_uri': users.create_logout_url('/')}),
    webapp2.Route('/api/user',handler=UserHandler),
    webapp2.Route('/api/drafts',handler=DraftListHandler),
    webapp2.Route('/api/drafts/<id:.*>',handler=DraftHandler),
    webapp2.Route('/api/templates',handler=TemplateListHandler),
    webapp2.Route('/api/templates/<id:.*>',handler=TemplateHandler),
    webapp2.Route('/api/tags', handler = TagsHandler),
    webapp2.Route('/api/usergroups', handler = GroupHandler),
    webapp2.Route('/api/admin/rebuildIndex', handler = IndexHandler),
    webapp2.Route('/api/admin/temp', handler = TempHandler)
    ], debug=True)

import datetime
import string
import logging
from google.appengine.ext import ndb
from google.appengine.api import users

def stringtodatetime(s):
    return datetime.datetime.strptime(string.split(s,'.')[0],
                                           "%Y-%m-%dT%H:%M:%S")
class UserGroup(ndb.Model):
    name = ndb.StringProperty(required=True)
    owners = ndb.UserProperty(repeated=True)
    members = ndb.UserProperty(repeated=True)

class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty()
    description = ndb.TextProperty()
    impact = ndb.TextProperty()
    documentation = ndb.TextProperty()
    rationale  = ndb.TextProperty()
    implementation_steps = ndb.TextProperty()    
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    technician = ndb.UserProperty()
    peer_reviewer = ndb.UserProperty()
    author = ndb.UserProperty()
    priority = ndb.StringProperty(choices=set(["sensitive", "routine"]))
    status = ndb.StringProperty(choices={'draft','created','approved'})
    audit_trail = ndb.JsonProperty()
    tests_conducted  = ndb.TextProperty()
    risks  = ndb.TextProperty()
    backout_plan  = ndb.TextProperty()
    communication_plan = ndb.TextProperty()
    layman_description = ndb.TextProperty()
    startTime = ndb.DateTimeProperty()
    endTime = ndb.DateTimeProperty()
    tags = ndb.StringProperty(repeated=True)
    def __setattr__(self, attr, value):
        if (attr in ['startTime','endTime','created_on']
            and isinstance(value, basestring)):
            d = stringtodatetime(value)
            object.__setattr__(self,attr,d)
        elif (attr in ['technician','peer_reviewer'] and isinstance(value, basestring)):
            d = users.User(value)
            object.__setattr__(self,attr,d)
        elif (attr == 'tags' and isinstance(value, basestring)):
            d= value.split(',')
            object.__setattr__(self,attr,d)
        else:
            object.__setattr__(self,attr,value)


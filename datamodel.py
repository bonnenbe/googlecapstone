import datetime
from google.appengine.ext import ndb
from google.appengine.api import users


class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty()
    description = ndb.TextProperty()
    impact = ndb.TextProperty()
    documentation = ndb.TextProperty()
    rationale  = ndb.TextProperty()
    implementation_steps = ndb.TextProperty()    
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    technician = ndb.StringProperty()
    author = ndb.UserProperty()
    priority = ndb.StringProperty(choices=set(["sensitive", "routine"]))
    audit_trail = ndb.JsonProperty()
    tests_conducted  = ndb.TextProperty()
    risks  = ndb.TextProperty()
    backout_plan  = ndb.TextProperty()
    communication_plan  = ndb.TextProperty()
    layman_description  = ndb.TextProperty()
    startTime = ndb.DateTimeProperty()
    endTime = ndb.DateTimeProperty()

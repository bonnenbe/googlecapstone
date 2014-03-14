import datetime
import string
import logging
from google.appengine.ext import ndb
from google.appengine.api import users, search


#directly editable properties
properties = {	
    'summary',
    'description',
    'impact',
    'documentation',
    'rationale',
    'implementation_steps',
    'technician',
    'peer_reviewer',
    'priority',
    'tests_conducted',
    'risks',
    'backout_plan',
    'communication_plan',
    'layman_description',
    'startTime',
    'endTime',
    'tags'
}

searchable_properties = properties | {
    'created_on',
    'author',
    'status'
}



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
            
    
    def toSearchDocument(self):
        
        fields = []
        for property in searchable_properties:
            attr = getattr(self, property)
            
            #todo: change some fields to atom fields (e.g. priority) for faster searching
            
            if property == "tags":
                #multifield
                for tag in attr:
                    logging.info(tag)
                    fields.append(search.TextField(name=property, value=tag))
                    
            elif isinstance(attr, datetime.datetime):
                fields.append(search.DateField(name=property, value=attr))
            elif isinstance(attr, users.User):
                fields.append(search.TextField(name=property, value=attr.email()))
            else:
                fields.append(search.TextField(name=property, value=attr))
        
        return search.Document(
            doc_id = self.key.urlsafe(),
            fields = fields
        )

#the key id should be a tag string
class Tag(ndb.Model):
    frequency = ndb.IntegerProperty(default=0)

    def toSearchDocument(self):
        tag = self.key.id()
        fields = []
        for i in range(1,len(tag)+1):
            for j in range(0,len(tag)-i):
                fields.append(search.AtomField(name='text', value=tag[j:j+i]))
        fields.append(search.NumberField(name='frequency', value=self.frequency))
        return search.Document(
            doc_id = tag,
            fields = fields,
            rank = self.frequency
            )

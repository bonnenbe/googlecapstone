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
    'tags',
    'cc_list'
}

searchable_properties = properties | {
    'created_on',
    'approved_on',
    'author',
    'status'
}



def stringtodatetime(s):
    return datetime.datetime.strptime(string.split(s,'.')[0],
                                           "%Y-%m-%dT%H:%M:%S")
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
def keyToIDs(key):
    return string.join(intersperse([str(pair[1]) for pair in key.pairs()], '-'))

class UserGroup(ndb.Model):
    name = ndb.StringProperty()
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
    approved_on = ndb.DateTimeProperty()
    technician = ndb.UserProperty()
    peer_reviewer = ndb.UserProperty()
    cc_list = ndb.UserProperty(repeated=True)
    author = ndb.UserProperty()
    priority = ndb.StringProperty(choices=set(["sensitive", "routine"]))
    status = ndb.StringProperty(choices={'draft','created','approved', 'succeeded', 'failed', 'template'})
    audit_trail = ndb.JsonProperty()
    tests_conducted  = ndb.TextProperty()
    risks  = ndb.TextProperty()
    backout_plan  = ndb.TextProperty()
    communication_plan = ndb.TextProperty()
    layman_description = ndb.TextProperty()
    startTime = ndb.DateTimeProperty()
    endTime = ndb.DateTimeProperty()
    tags = ndb.StringProperty(repeated=True)

    def id(self):
        return keyToIDs(self.key)

    def __setattr__(self, attr, value):
        if (attr in ['startTime','endTime','created_on']
            and isinstance(value, basestring)):
            d = stringtodatetime(value)
            object.__setattr__(self,attr,d)
        elif (attr in ['technician','peer_reviewer','author','cc_list'] and isinstance(value, basestring)):
            d = users.User(value)
            object.__setattr__(self,attr,d)
        elif (attr in ['technician','peer_reviewer','author','cc_list'] and isinstance(value, list)
              and len(value) > 0 and isinstance(value[0], basestring)):
            object.__setattr__(self,attr,[users.User(s) for s in value])
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
            elif property == 'cc_list':
                for user in attr:
                    fields.append(search.TextField(name=property, value=user.email()))
                    fields.append(search.AtomField(name=property, value=user.email()))
            elif isinstance(attr, datetime.datetime):
                fields.append(search.DateField(name=property, value=attr))
            elif isinstance(attr, users.User):
                fields.append(search.TextField(name=property, value=attr.email()))
                fields.append(search.AtomField(name=property, value=attr.email()))
            else:
                fields.append(search.TextField(name=property, value=attr))
        
        fields.append(search.TextField(name='id', value=self.id()))
        return search.Document(
            doc_id = self.key.urlsafe(),
            fields = fields,
            rank = int((self.created_on - datetime.datetime(1970,1,1)).total_seconds())
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

import datetime
from google.appengine.ext import db
from google.appengine.api import users

class ChangeRequest(db.Model):
    summary = db.TextProperty(required=True)
    description = db.TextProperty(required=True)
    impact = db.TextProperty(required=True)
    documentation = db.TextProperty(required=True)
    rationale  = db.TextProperty(required=True)
    implementation_steps = db.TextProperty(required=True)    
    tests_conducted  = db.TextProperty(required=True)
    risks  = db.TextProperty(required=True)
    backout_plan  = db.TextProperty(required=True)
    communication_plan  = db.TextProperty(required=True)
    layman_description  = db.TextProperty(required=True)
    verification_steps  = db.TextProperty(required=True)
    status = db.StringProperty(required=True,
                               choices=set(["approved", "awaiting approval", "complete"]))
    approver = db.StringProperty(required=True)
    sync_to_helpdesk  = db.BooleanProperty(required=True)
    priority = db.StringProperty(required=True,
                               choices=set(["sensitive", "low", "none"]))
    created_on = DateProperty()
    timezone = db.StringProperty(required=True,
                                 choices-set([...]))
    start_time = DateTimeProperty()
    end_time = DateTimeProperty()
    blackout_duration = db.StringProperty()
    group = db.StringProperty()
    cc_list = db.ListProperty(db.StringProperty())
    technician = db.StringProperty()
    peer_reviewer = db.StringProperty()
    services_affected = db.StringProperty()
    locations_affected = db.StringProperty()
    components = ...
    users_affected = db.StringProperty(required=True,
                               choices=set(["large > 1000" ...]))
    region_affected_low_impact_time = db.BooleanProperty()
    worklog = ...
    audit_trail = ...
                                       
                                   

    
    

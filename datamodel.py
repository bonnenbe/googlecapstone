import datetime

class ChangeRequest(db.Model):
    int id
    summary = db.Text(required=True)
    description = db.Text(required=True)
    impact = db.Text(required=True)
    documentation = db.Text(required=True)
    rationale  = db.Text(required=True)
    implementation_steps = db.Text(required=True)    
    tests_conducted  = db.Text(required=True)
    risks  = db.Text(required=True)
    backout_plan  = db.Text(required=True)
    communication_plan  = db.Text(required=True)
    layman_description  = db.Text(required=True)
    verification_steps  = db.Text(required=True)
    status = db.StringProperty(required=True,
                               choices=set(["approved", "awaiting approval", "complete"]))
    approver = db.StringProperty(required=True)
    sync_to_helpdesk  = db.BooleanProperty(required=True)
    priority = db.StringProperty(required=True,
                               choices=set(["sensitive", "low", "none"]))
    created_on = datetime.date
    timezone = db.StringProperty(required=True,
                                 ...)
    start_time = datetime.datetime
    end_time = datetime.datetime
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
                                       
                                   

    
    

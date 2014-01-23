import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

import datetime



class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty(required=True)
    description = ndb.TextProperty(required=True)
    impact = ndb.TextProperty(required=True)
    documentation = ndb.TextProperty(required=True)
    rationale  = ndb.TextProperty(required=True)
    implementation_steps = ndb.TextProperty(required=True)    
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    technician = ndb.UserProperty()
    priority = ndb.StringProperty(required=True,
                                  choices=set(["sensitive", "routine"]))


MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/submit" method="post">
      <p>
      Summary: <div><textarea name="summary" rows="3" cols="60"></textarea></div>
      Description: <div><textarea name="description" rows="3" cols="60"></textarea></div>
Impact: <div><textarea name="description" rows="3" cols="60"></textarea></div>
Documentation: <div><textarea name="documentation" rows="3" cols="60"></textarea></div>
Rationale: <div><textarea name="rationale" rows="3" cols="60"></textarea></div>
Implementation Steps: <div><textarea name="implementation_steps" rows="3" cols="60"></textarea></div>
Priority: <div><select name="priority">
<option value="sensitive">sensitive</option>
<option value="routine">routine</option>
      <div><input type="submit" value="Submit Change Request"></div>
</p>
    </form>
    <hr>
    <a href="%s">%s</a>
  </body>
</html>
"""

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return ndb.Key('Guestbook', guestbook_name)



class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write('<html><body>')
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        crs_query = ChangeRequest.query(
            ancestor=guestbook_key(guestbook_name)).order(-ChangeRequest.created_on)
        crs = crs_query.fetch(10)

        for cr in crs:
            self.response.write('On %s ' % cr.created_on)
            if cr.technician:
                self.response.write(
                        '<b>%s</b> submitted:' % cr.technician.nickname())
            else:
                self.response.write('an anonymous person submitted:')
            self.response.write('<blockquote>%s</blockquote>\
<blockquote>%s</blockquote>\
<blockquote>%s</blockquote>\
<blockquote>%s</blockquote>\
<blockquote>%s</blockquote>\
<blockquote>%s</blockquote>\
                                <blockquote>%s</blockquote>' %
                                (cgi.escape(cr.summary),cgi.escape(cr.description),
                                 cgi.escape(cr.impact),cgi.escape(cr.documentation),
                                 cgi.escape(cr.rationale),cgi.escape(cr.implementation_steps),
                                 cgi.escape(cr.priority)))
            
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # Write the submission form and the footer of the page
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %
                            (url, url_linktext))


class Guestbook(webapp2.RequestHandler):

    def post(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        cr = ChangeRequest(parent=guestbook_key(guestbook_name))
                           
                           
                           

        if users.get_current_user():
            cr.technician = users.get_current_user()

        cr.summary = self.request.get('summary')
        cr.description = self.request.get('description')
        cr.impact = self.request.get('impact')
        cr.documentation = self.request.get('documentation')
        cr.rationale = self.request.get('rationale')
        cr.implementation_steps = self.request.get('implementation_steps')
        cr.priority = self.request.get('priority')
        cr.put()


        self.redirect('/')


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit', Guestbook),
], debug=True)

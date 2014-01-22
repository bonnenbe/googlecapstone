import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

import datetime



class ChangeRequest(ndb.Model):
    summary = ndb.TextProperty(required=True)
    created_on = ndb.DateTimeProperty(auto_now_add=True)
    technician = ndb.UserProperty()

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/sign?%s" method="post">
      <div><textarea name="summary" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Submit Change Request"></div>
    </form>

    <hr>

    <form>Guestbook name:
      <input value="%s" name="guestbook_name">
      <input type="submit" value="switch">
    </form>

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
                        '<b>%s</b> wrote:' % cr.technician.nickname())
            else:
                self.response.write('an anonymous person wrote:')
            self.response.write('<blockquote>%s</blockquote>' %
                                cgi.escape(cr.summary))
            
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # Write the submission form and the footer of the page
        sign_query_params = urllib.urlencode({'guestbook_name': guestbook_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %
                            (sign_query_params, cgi.escape(guestbook_name),
                             url, url_linktext))


class Guestbook(webapp2.RequestHandler):

    def post(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        cr = ChangeRequest(parent=guestbook_key(guestbook_name),
                           summary=self.request.get('summary'))
                           
                           

        if users.get_current_user():
            cr.technician = users.get_current_user()

        cr.summary = self.request.get('summary')
        cr.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Guestbook),
], debug=True)

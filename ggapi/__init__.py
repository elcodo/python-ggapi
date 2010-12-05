#! /usr/bin/env python
#
# python-ggapi - Python bindings for the GG.pl REST API
#
# Copyright (c) 2010, Grzegorz Bialy, ELCODO.pl
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import urllib
import urllib2

try:
    import json as simplejson
except ImportError:
    try:
        import simplejson
    except ImportError:
        try:
            from django.utils import simplejson
        except ImportError:
            try:
                import jsonlib as simplejson
                simplejson.loads
            except (ImportError, AttributeError):
                raise Exception("Module SimpleJSON cannot be imported.")

__all__ = ['GG']

VERSION = '0.1'

REQUEST_TOKEN_URL = 'https://auth.api.gg.pl/token'
AUTHORIZE_URL = 'https://www.gg.pl/authorize'

SCOPE_PUBDIR_URL = 'https://pubdir.api.gg.pl'
SCOPE_USERS_URL = 'https://users.api.gg.pl'
SCOPE_LIFE_URL = 'https://life.api.gg.pl'

RESPONSE_TYPE = "json"


class GGError(Exception):
    """Exceptions for errors from GG"""

    def __init__(self, code, msg, args=None):
        self.code = code
        self.msg = msg
        self.args = args

    def __unicode__(self):
        return 'Error %s: %s' % (self.code, self.msg)


class GG(object):

    def __init__(self, client_id, client_secret, redirect_uri, code=None,
        access_token=None, refresh_token=None):
        """Initialize class with required information.

        NOTE: You must provide stored access token or code to generate one.
        """
        if not code and not (access_token and refresh_token):
            raise Exception(u"You must provide either code or access token " \
                u"and refresh token.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        if code:
            self.access_token, self.refresh_token = \
                self._get_access_token(code)
        if access_token:
            self.access_token = access_token
            self.refresh_token = refresh_token

    def _format_uin(self, uin=None):
        """Format UIN for request.

        If uin is None return 'me' according to GG API.
        """
        if not uin:
            return "me"
        return "user,%d" % uin

    def _do_request(self, url, method, data=None):
        """Do request to REST API.

        NOTE: Method is unused now as none of API methods use DELETE, PUT, etc.
        """
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "User-Agent": "python-ggapi v%s" % VERSION,
            "Accept": RESPONSE_TYPE,
        }

        # add oauth header if access token exist
        try:
            if self.access_token:
                headers['Authorization'] = 'OAuth %s' % self.access_token
        except AttributeError:
            pass

        try:
            req = urllib2.Request(
                url=url,
                data=urllib.urlencode(data) if data else None,
                headers=headers)
            resp = urllib2.urlopen(req)
        except urllib2.HTTPError, http_error:
            if http_error.code in (400, 409, ):
                result = simplejson.loads(http_error.read())
                raise GGError(result['error'], result['error_description'],
                    args=data)
            elif "expired_token" in http_error.read():
                self._refresh_token()
                return self._do_request(url, method, data)
            else:
                raise http_error
        return resp.read()

    def _get_access_token(self, code):
        """Get access token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri,
            'grant_type': u"authorization_code",
        }

        resp = self._do_request(REQUEST_TOKEN_URL, method="POST", data=data)
        result = simplejson.load(resp)
        return (result['access_token'], result['refresh_token'])

    def _refresh_token(self, refresh_token):
        """Refresh token"""
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'redirect_uri': self.redirect_uri,
            'grant_type': u"authorization_code",
        }

        resp = self._do_request(REQUEST_TOKEN_URL, method="POST", data=data)
        result = simplejson.loads(resp)
        return (result['access_token'], result['refresh_token'])

    def get_tokens(self):
        """Returns access_token and refresh_token"""
        return (self.access_token, self.refresh_token)

    def get_user(self, uin=None):
        """Get user from public directory"""
        url = u"%s/users/%s" % (SCOPE_PUBDIR_URL, self._format_uin(uin))
        result = simplejson.loads(self._do_request(url, method="GET"))
        return result['result']

    def get_friends(self, uin=None, limit=1000, last_id=None):
        """Get friends of user."""
        url = u"%s/friends/%s?limit=%d" % \
            (SCOPE_USERS_URL, self._format_uin(uin), limit)
        if last_id:
            url += u"&lastId=%d" % lastId
        result = simplejson.loads(self._do_request(url, method="GET"))
        return result['result']

    def send_notification(self, user, message, link=None):
        """Send notification message to user(s).
        Returns True if message was send.

        NOTE: user is either int (uin) or "friends".
        """
        url = u"%s/notification.%s" % (SCOPE_LIFE_URL, RESPONSE_TYPE)

        if isinstance(user, int):
            user = "user,%d" % user

        data = {
            'to': user,
            'message': message,
        }
        if link:
            data['link'] = link

        resp = self._do_request(url, method="POST", data=data)
        result = simplejson.loads(resp)
        if result['result']['status'] == 0:
            return True
        return False

    def send_event(self, message, link=None, image=None):
        """Post event on authorized user dashboard.
        Returns True if message is posted.

        """
        url = u"%s/event.%s" % (SCOPE_LIFE_URL, RESPONSE_TYPE)
        data = {
            'message': message,
        }
        if link:
            data['link'] = link
        if image:
            data['image'] = image

        resp = self._do_request(url, method="POST", data=data)
        result = simplejson.loads(resp)
        if result['result']['status'] == 0:
            return True
        return False

    def get_avatar_url(self, uin):
        """Get avatar URL of user with given UIN"""
        return "http://avatars.gg.pl/%d" % uin

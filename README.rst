============
python-ggapi
============

Python client library for GG.pl REST API.

Author
------
Grzegorz Biały (https://github.com/grzegorzbialy/)
ELCODO (http://elcodo.pl)

Install
-------
You can do one of the following:
* python setup.py install
* copy ggapi to anywhere to your PYTHONPATH (e.g. your project directory)

Usage
-----

You must provide one of the following when creating GG class:

1. code - only when user authorizes your app, GG.pl sends GET request with "code" parameter to your app,
2. access_token, refresh_token - stored in your storage (db, session, etc.) for returning user.

More info on authentication: http://dev.gg.pl/api/pages/ggapi/auth.html (Polish)

Library implements following methods:

*get_user(uin=None)*
    Gets user data from public directory. If uin is None it will get authorized user data.

    Returns dict.

*get_friends(uin=None, limit=1000, last_id=None)*
    Gets friends of user given by uin (if None, authorized user) according to limit and offset (last_id indicates id of previous query last record)

    Returns dict.

*send_notification(user, message, link=None)*
    Send notification to user with message and optional link.
    If user is int it is UIN, it can be "friends" to send to all friends.

    Returns True if notification was send, False otherwise.

*send_event(user, message, link=None, image=None)*
    Send event to authorized user dashboard.
    Link and image are optional. Image can be URL to file or base64.

    Returns True if event was send, False otherwise.

*get_avatar_url(uin)*
    URL of user avatar

Example
-------

Quick Django example view::

    from ggapi import GG

    CLIENT_ID = ""
    CLIENT_SECRET = ""
    REDIRECT_URI = ""


    def test(request):
        if "code" in request.GET:
            gg = GG(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                code=request.GET["code"], redirect_uri=REDIRECT_URI)
            access_token, refresh_token = gg.get_tokens()
        else:
            access_token, refresh_token = (...)your logic, e.g. get from SESSION(...)
            gg = GG(client_id=CLIENT_ID, client_secret=CLIENT_SECRET,
                access_token=access_token, refresh_token=refresh_token,
                redirect_uri=REDIRECT_URI)

        friend_list = gg.get_friends()
        my_info = gg.get_user()
        other_info = gg.get_user(2080)

        if gg.send_notification(2080, "Notification", "http://elcodo.pl"):
            # Notification send, yay!
            pass

        if gg.send_event(message="Dashboard message"):
            # Posted to my dashboard!
            pass

License
-------
OSI - The BSD License (http://www.opensource.org/licenses/bsd-license.php)


Copyright (c) 2010, Grzegorz Bialy, ELCODO.pl
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of the author nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS "AS IS" AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
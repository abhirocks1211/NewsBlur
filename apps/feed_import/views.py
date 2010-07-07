# -*- coding: utf-8 -*-
import urlparse
import oauth2 as oauth
from django.contrib.sites.models import Site
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth import login as login_user
from django.shortcuts import render_to_response
from apps.reader.forms import SignupForm
from apps.reader.models import UserSubscription
from apps.feed_import.models import OAuthToken, OPMLImporter, GoogleReaderImporter
from utils import json


def opml_upload(request):
    xml_opml = None
    message = "OK"
    code = 1
    payload = {}
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            file = request.FILES['file']
            xml_opml = file.read()
            
            opml_importer = OPMLImporter(xml_opml, request.user)
            folders = opml_importer.process()

            feeds = UserSubscription.objects.filter(user=request.user).values()
            payload = dict(folders=folders, feeds=feeds)
        else:
            message = "Attach an .opml file."
            code = -1
            
    data = json.encode(dict(message=message, code=code, payload=payload))
    return HttpResponse(data, mimetype='text/plain')

        
def reader_authorize(request):
    print request.session.session_key
    oauth_key = settings.OAUTH_KEY
    oauth_secret = settings.OAUTH_SECRET
    scope = "http://www.google.com/reader/api"
    request_token_url = ("https://www.google.com/accounts/OAuthGetRequestToken?"
                         "scope=%s&oauth_callback=http://%s%s") % (
                            scope,
                            Site.objects.get_current().domain,
                            reverse('opml-reader-callback'),
                         )
    authorize_url = 'https://www.google.com/accounts/OAuthAuthorizeToken'
    
    # Grab request token from Google's OAuth
    consumer = oauth.Consumer(oauth_key, oauth_secret)
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, "GET")
    request_token = dict(urlparse.parse_qsl(content))
    
    # Save request token and delete old tokens
    auth_token_dict = dict(request_token=request_token['oauth_token'], 
                           request_token_secret=request_token['oauth_token_secret'])
    if request.user.is_authenticated():
        OAuthToken.objects.filter(user=request.user).delete()
        auth_token_dict['user'] = request.user
    else:
        OAuthToken.objects.filter(session_id=request.session.session_key).delete()
        auth_token_dict['session_id'] = request.session.session_key
    OAuthToken.objects.create(**auth_token_dict)
                              
    redirect = "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
    return HttpResponseRedirect(redirect)

def reader_callback(request):
    access_token_url = 'https://www.google.com/accounts/OAuthGetAccessToken'
    consumer = oauth.Consumer(settings.OAUTH_KEY, settings.OAUTH_SECRET)

    if request.user.is_authenticated():
        user_token = OAuthToken.objects.get(user=request.user)
    else:
        print request.session.session_key
        user_token = OAuthToken.objects.get(session_id=request.session.session_key)

    # Authenticated in Google, so verify and fetch access tokens
    token = oauth.Token(user_token.request_token, user_token.request_token_secret)
    token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)
    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    user_token.access_token = access_token['oauth_token']
    user_token.access_token_secret = access_token['oauth_token_secret']
    user_token.save()
    
    # Fetch imported feeds on next page load
    request.session['import_from_google_reader'] = True
    
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    
    return HttpResponseRedirect(reverse('import-signup'))
    
def import_from_google_reader(user):
    scope = "http://www.google.com/reader/api"
    sub_url = "%s/0/subscription/list" % scope

    if user.is_authenticated():
        user_tokens = OAuthToken.objects.filter(user=user)
        if user_tokens.count():
            user_token = user_tokens[0]
            consumer = oauth.Consumer(settings.OAUTH_KEY, settings.OAUTH_SECRET)
            token = oauth.Token(user_token.access_token, user_token.access_token_secret)
            client = oauth.Client(consumer, token)

            resp, content = client.request(sub_url, 'GET')
            reader_importer = GoogleReaderImporter(content, user)
            return reader_importer.process()

def import_signup(request):
    if request.method == "POST":
        signup_form = SignupForm(prefix='signup', data=request.POST)
        if signup_form.is_valid():
            new_user = signup_form.save()
            user_token = OAuthToken.objects.get(session_id=request.session.session_key)
            user_token.user = new_user
            user_token.save()
            login_user(request, new_user)
            return HttpResponseRedirect(reverse('index'))
    else:
        signup_form = SignupForm(prefix='signup')

    return render_to_response('import/signup.xhtml', {
        'signup_form': signup_form,
    }, context_instance=RequestContext(request))
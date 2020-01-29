from flask import current_app,url_for,redirect, session,request
from rauth import OAuth1Service,OAuth2Service
import json

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']
        self.consumer_public_secret = credentials.get('public',None)

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url="https://graph.facebook.com/oauth/authorize",
            access_token_url="https://graph.facebook.com/oauth/access_token",
            base_url="https://graph.facebook.com/"
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.get('me').json()
        return (
            'facebook$' + me['id'],
            me.get('name'),
            me.get('email')
        )

# class TwitterSignIn(OAuthSignIn):
#     #нету ключей
#     def __init__(self):
#         super(TwitterSignIn, self).__init__('twitter')
#         self.service = OAuth1Service(
#             name='twitter',
#             consumer_key=self.consumer_id,
#             consumer_secret=self.consumer_secret,
#             request_token_url='https://api.twitter.com/oauth/request_token',
#             authorize_url='https://api.twitter.com/oauth/authorize',
#             access_token_url='https://api.twitter.com/oauth/access_token',
#             base_url='https://api.twitter.com/1.1/'
#         )
#
#     def authorize(self):
#         request_token = self.service.get_request_token(
#             params={'oauth_callback': self.get_callback_url()}
#         )
#         session['request_token'] = request_token
#         return redirect(self.service.get_authorize_url(request_token[0]))
#
#     def callback(self):
#         request_token = session.pop('request_token')
#         if 'oauth_verifier' not in request.args:
#             return None, None, None
#         oauth_session = self.service.get_auth_session(
#             request_token[0],
#             request_token[1],
#             data={'oauth_verifier': request.args['oauth_verifier']}
#         )
#         me = oauth_session.get('account/verify_credentials.json').json()
#         social_id = 'twitter$' + str(me.get('id'))
#         username = me.get('screen_name')
#         return social_id, username, None
#
# class InstagramSigIn(OAuthSignIn):
#     #нету ключей
#     def __init__(self):
#         super(InstagramSigIn, self).__init__('instagram')
#         self.service = OAuth2Service(
#             name='instagram',
#             client_id=self.consumer_id,
#             client_secret=self.consumer_secret,
#             authorize_url='https://api.instagram.com/oauth/authorize',
#             access_token_url='https://api.instagram.com/oauth/access_token',
#             base_url='https://api.instagram.com/'
#         )
#
#     def authorize(self):
#         return redirect(self.service.get_authorize_url(
#             scope='basic',
#             response_type='code',
#             redirect_uri=self.get_callback_url())
#         )
#
#     def callback(self):
#         if 'code' not in request.args:
#             return None, None, None
#         oauth_session = self.service.get_auth_session(
#             data={'oauth_verifier': request.args['oauth_verifier']}
#         )
#         me = oauth_session.get('me').json()
#         return (
#             'instagram$' + me['id'],
#             me.get('username'),
#             None,
#             me.get('full_name')
#         )

class VkSignIn(OAuthSignIn):
    def __init__(self):
        super(VkSignIn, self).__init__('vk')
        self.service = OAuth2Service(
            name='vk',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://oauth.vk.com/authorize',
            access_token_url='https://oauth.vk.com/access_token',
            base_url='https://oauth.vk.com/'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            client_id=self.consumer_id,
            scope='email',
            response_type='code',
            display='popup',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        me = oauth_session.access_token_response.json()
        email = me['email']
        user_id = me['user_id']
        params = {
            'user_ids':user_id,
            'fields': 'is_closed,first_name,last_name,nickname,screen_name,sex,bdate,city',
            'access_token': oauth_session.access_token,
            'v': 5.103
        }
        user_info = oauth_session.get('https://api.vk.com/method/users.get',params=params).json()
        return (
            'vk' + str(user_id),
            user_info['response'][0]['last_name'] + ' ' + user_info['response'][0]['first_name'],
            email
        )

class OkSignIn(OAuthSignIn):
    def __init__(self):
        super(OkSignIn, self).__init__('ok')
        self.client_public_secret = self.consumer_public_secret
        self.service = OAuth2Service(
            name='ok',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://connect.ok.ru/oauth/authorize',
            access_token_url='https://api.ok.ru/oauth/token.do',
            base_url='https://api.ok.ru/fb.do'
        )
    def authorize(self):
        return redirect(self.service.get_authorize_url(
            client_id= self.consumer_id,
            scope="GET_EMAIL",
            response_type="code",
            redirect_uri = self.get_callback_url())
        )
    def get_sign(self,public,access_token,secret_key):
        from hashlib import md5
        first = f'application_key={public}method=users.getCurrentUser'
        sec_hex = md5(f"{access_token}{secret_key}".encode('utf-8')).hexdigest()
        first += sec_hex
        return md5(first.encode('utf-8')).hexdigest()

    def callback(self):
        def decode_json(payload):
            return json.loads(payload.decode('utf-8'))

        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()},
            decoder=decode_json
        )
        params = {
            'method': 'users.getCurrentUser',
            'access_token': oauth_session.access_token,
            'application_key': self.consumer_public_secret,
            'sig': self.get_sign(self.consumer_public_secret,oauth_session.access_token,self.consumer_secret)
        }
        me = oauth_session.get('https://api.ok.ru/fb.do',params=params).json()
        # print(me)
        return (
            'ok' + me['uid'],
            me['name'],
            None
        )
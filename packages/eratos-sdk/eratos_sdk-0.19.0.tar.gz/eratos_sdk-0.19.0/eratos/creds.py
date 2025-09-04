#
# Copyright (C) Eratos Group Pty Ltd and its affiliates.
#
# This file was created as part of:
#
#   Eratos Python SDK
#
# It is proprietary software, you may not:
#
#   a) redistribute it and/or modify without permission from Eratos Group Pty Ltd.
#   b) reuse the code in part or in full without permission from Eratos Group Pty Ltd.
#
# If permission has been granted for reuse and/or redistribution it is subject
# to the following conditions:
#
#   a) The above copyright notice and this permission notice shall be included
#      in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import logging
from urllib.parse import urlparse
from datetime import datetime
import hashlib
import hmac
import base64
import platform
import time
import secrets
import jwt
import os
from requests import Session

from yaml import load as yload
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from .ern import Ern
from . import __tracker__

_logger = logging.getLogger(__name__)

class BaseCreds:
    """
    A base credentials class to interact with the tracker node.
    """
    def __init__(self, tracker: str=__tracker__):
        self._tracker = tracker.strip()
        tr = tracker.strip()
        if tr.startswith("https://"):
            self._tracker = urlparse(tr).netloc
        else:
            self._tracker = tr
        self._tracker_url = 'https://' + self._tracker

    def tracker(self):
        """
        Retrieves the tracker.
        
        Returns
        -------
        str
            The string for the tracker node.
        """
        return self._tracker

    def tracker_url(self):
        """
        Retrieves the tracker url.
        
        Returns
        -------
        str
            The string for the tracker url.
        """
        return self._tracker_url

    def auth_query_params(self):
        raise NotImplementedError()

class AccessTokenCreds(BaseCreds):
    """
    A class to interact with access credentials. Inherits from the BaseCreds class. 
    """
    def __init__(self, id: str, secret: str, tracker: str=__tracker__):
        super().__init__(tracker=tracker)
        self._id = id
        self._secret = base64.b64decode(secret.strip())

    def auth_query_params(self):
        """
        Gets the authentication query parameter for a user/account.
        
        Returns
        -------
        dict
            A dictionary containing the key 'user_sig' and the encoded JSON web token value.
        """
        # Construct the JWT signed using the client_secret.
        now = int(time.time())
        jti = base64.b32encode(secrets.token_bytes(15)).decode('ascii')
        jwt_payload = {
            'iat': now,
            'exp': now + 600, # 5 min from now
            'jti': jti,
        }
        encoded_jwt = jwt.encode(jwt_payload, self._secret, algorithm='HS256', headers={'kid': self._id, 'eratos.com/tracker': self.tracker().split(":")[0] })
        return {'user_sig': encoded_jwt}


class AccessBearerCreds(BaseCreds):
    """
    A class to interact with oauth bearer credentials. Inherits from the BaseCreds class. 
    """
    def __init__(self, token: str, tracker: str=__tracker__):
        super().__init__(tracker=tracker)
        self._token = token

    def auth_query_params(self):
        """
        Gets the authentication query parameter for a user/account.

        Returns
        -------
        dict
            A dictionary containing the key 'oauth_token' and the encoded JSON web token value.
        """
        return {'oauth_token': self._token}


class JobKeyCreds(BaseCreds):
    """
    A class to interact with job key authentication. Inherits from the BaseCreds class. 
    """
    def __init__(self, key: str, tracker: str=__tracker__):
        super().__init__(tracker=tracker)
        self._key = key
    
    def auth_query_params(self):
        """
        Gets the authentication query parameter for a job.
        
        Returns
        -------
        dict
            A dictionary containing the key 'user_sig' and the job key.
        """
        return {'job_key': self._key}

class RequestTokenInserter:
    """
    A class to interact with the authorization token.
    """
    def __init__(self, token: str):
        self._token = token
        
    def __call__(self, r):
        # Attach the token as a an auth header.
        r.headers['Authorization'] = 'Bearer %s' % self._token
        return r

class TrackerExchange:
    """
    A class to interact with the Eratos tracker exchange node.
    """
    def __init__(self, session: Session, creds: AccessTokenCreds=None, ignore_certs=False):
        self._session = session
        self._hosts = {}
        self._ignore_certs = ignore_certs
        self._tokens = {}
        if creds is None:
            # Attempt to load creds from .eratos credentials.
            self._attempt_load_user_creds()
        else:
            self._creds = creds
        self._master_pn = None
        self._fetch_master_pn()

    def get_auth_token(self, target_ern: Ern):
        """
        Retrieves the authentication token for a given ERN.

        Parameters
        ----------
        target_ern : Ern
            The unique Eratos Resource Name (ERN).
        
        Returns
        -------
        RequestTokenInserter
            Returns the authentication token inserter class for a given ERN.
        """
        return RequestTokenInserter(self._refresh_token(target_ern)['token'])

    def master_pn(self):
        """
        Retrieves the Eratos Resource Name (ERN) for the master primary node.
        
        Returns
        -------
        Ern
            The unique Eratos Resource Name (ERN) of the master primary node.
        """
        return self._master_pn

    def _fetch_master_pn(self):
        if self._master_pn is not None:
            return
        req = self._session.request('GET', self._creds.tracker_url()+'/info', verify=not self._ignore_certs)
        if req.status_code >= 200 and req.status_code < 400:
            req_data = req.json()
            self._master_pn = Ern(ern=req_data['masterPrimaryNode'])
        else:
            _logger.error('tracker exchange: status for master pn: %d: %s' % (req.status_code, req.text))
            raise Exception(req.text)

    def _attempt_load_user_creds(self):
        if platform.system() == 'Windows':
            basedir = os.path.join(os.getenv('LocalAppData'), 'eratos')
        else:
            basedir = os.path.join(os.getenv('HOME'), '.eratos')
        cred_path = os.path.join(basedir, 'credentials.yaml')
        if not os.path.exists(cred_path):
            raise Exception('no global Eratos credentials defined, pass in creds to Adapter or login using the Eratos CLI')
        with open(cred_path, 'rt') as f:
            cred_content = yload(f.read(), Loader=Loader)
        if 'tracker' not in cred_content or type(cred_content['tracker']) is not str:
            raise Exception('invalid user credential content in %s' % cred_path)
        if 'keyId' not in cred_content or type(cred_content['keyId']) is not str:
            raise Exception('invalid user credential content in %s' % cred_path)
        if 'secret' not in cred_content or type(cred_content['secret']) is not str:
            raise Exception('invalid user credential content in %s' % cred_path)
        self._creds = AccessTokenCreds(cred_content['keyId'], cred_content['secret'], cred_content['tracker'])

    def fetch_target_host(self, target_ern: Ern):
        """
        Retrieves the host for a given ERN.

        Parameters
        ----------
        target_ern : Ern
            The unique Eratos Resource Name (ERN).
        
        Returns
        -------
        str
            The URL or ID string (ERN) for the host location.
        """
        target_ern_str = target_ern.root().__str__()
        _logger.debug('tracker exchange: requesting host for %s' % target_ern_str)
        if target_ern_str not in self._hosts:
            if target_ern.type() == 'tracker':
                return self._creds.tracker_url()
            elif target_ern.type() == 'node':
                req = self._session.request('GET', self._creds.tracker_url()+'/nodes/%s'%target_ern.id(), verify=not self._ignore_certs)
                if req.status_code >= 200 and req.status_code < 400:
                    req_data = req.json()
                    nodeHostName = req_data['conn']['domain'] if 'domain' in req_data['conn'] else req_data['conn']['host']
                    if req_data['conn']['httpPort'] == 443:
                        self._hosts[target_ern_str] = 'https://' + nodeHostName
                    else:
                        self._hosts[target_ern_str] = 'https://%s:%d' % (nodeHostName, req_data['conn']['httpPort'])
                else:
                    _logger.error('tracker exchange: status for %s: %d: %s' % (target_ern_str, req.status_code, req.text))
                    raise Exception(req.text)
            else:
                raise Exception('cannot fetch host for ern %s: invalid type' % target_ern)
            _logger.debug('tracker exchange: found host for %s: %s' % (target_ern_str, self._hosts[target_ern_str]))
        return self._hosts[target_ern_str]

    def _refresh_token(self, target_ern: Ern):
        target_ern_str = target_ern.root().__str__()
        now = int(time.time())
        if target_ern_str not in self._tokens or (self._tokens[target_ern_str]['exp'] - 10) < now:
            _logger.debug('tracker exchange: refreshing token for %s' % target_ern_str)
            # Construct the JWT signed using the client_secret.
            cred_params = self._creds.auth_query_params()
            req = self._session.request('GET', self._creds.tracker_url()+'/auth/token', params={'comm_ern': target_ern_str, **cred_params}, verify=not self._ignore_certs)
            if req.status_code >= 200 and req.status_code < 400:
                self._tokens[target_ern_str] = {
                    'token': req.text,
                    'exp': jwt.decode(req.text, options={ 'verify_signature': False })['exp'] - 10 # Take 10 seconds off of the expiary.
                }
                _logger.debug('tracker exchange: new user token for %s: %s' % (target_ern_str,self._tokens[target_ern_str]['token']))
                _logger.debug('tracker exchange: new user token for %s expires at: %d' % (target_ern_str,self._tokens[target_ern_str]['exp']))
            else:
                _logger.error('tracker exchange: status for %s: %d: %s' % (target_ern_str, req.status_code, req.text))
                raise Exception(req.text)
        return self._tokens[target_ern_str]

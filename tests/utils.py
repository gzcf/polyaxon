# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import datetime
import json
import tempfile
import uuid
import redis

from urllib.parse import urlparse
from unittest.mock import patch


from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.db import connections
from django.test import Client, TestCase, TransactionTestCase
from django.test.client import FakePayload
from rest_framework import status

from rest_framework.authtoken.models import Token

from polyaxon.config_settings import RedisPools
from factories.factory_users import UserFactory

# Stores the currently valid tokens to check against
_valid_tokens = dict()
CONTENT_TYPE_APPLICATION_JSON = 'application/json'


class AuthorizedClient(Client):
    """Class to instantiate an authorized client.

     This is allowed to make calls to the authenticated endpoints.
     """

    def __init__(self, access_token='', authentication_type='Token', **defaults):
        super().__init__(**defaults)
        user = defaults.get('user', UserFactory())
        self.login_user(user, access_token, authentication_type)

    def login_user(self, user, access_token='', authentication_type='Token'):
        self.user = user
        self.expires = datetime.datetime.now() + datetime.timedelta(days=1)
        if not access_token:
            token, _ = Token.objects.get_or_create(user=self.user)
            self.access_token = token.key
        else:
            self.access_token = access_token

        if self.user and self.access_token:
            self.patch_validate_token()

        self.authorization_header = '{} {}'.format(authentication_type, self.access_token)

    def patch_validate_token(self,
                             username=None,
                             access_token=None,
                             feature_flags=None,
                             status_code=200):
        # Use the objects user and access_token if none provided
        if username is None:
            username = self.user.username
        if access_token is None:
            access_token = self.access_token

        # Put the current access_token into the dict of valid ones
        _valid_tokens[access_token] = dict(
            username=username,
            feature_flags=feature_flags,
            status_dode=status_code
        )

    def _invalidate_token(self):
        # Remove the current access_token
        del _valid_tokens[self.access_token]

    def request(self, **request):
        updated_request = {'HTTP_AUTHORIZATION': self.authorization_header}
        if 'HTTP_X_REQUEST_ID' not in request:
            request['HTTP_X_REQUEST_ID'] = str(uuid.uuid4())

        updated_request.update(request)
        return super().request(**updated_request)

    def do_request(self,
                   method,
                   path,
                   data=None,
                   content_type=CONTENT_TYPE_APPLICATION_JSON,
                   **extra):
        if data is None:
            data = {}

        for key, value in data.items():
            # Fix UUIDs for convenience
            if isinstance(value, uuid.UUID):
                data[key] = value.hex

            # Fix datetimes
            if isinstance(value, datetime.datetime):
                data[key] = value.strftime('%Y-%m-%d %H:%M')

        if content_type == CONTENT_TYPE_APPLICATION_JSON:
            data = json.dumps(data)

        request = self.encode_data(method, path, data, content_type, **extra)
        return self.request(**request)

    def put(self, path, data=None, content_type=CONTENT_TYPE_APPLICATION_JSON, **extra):
        """Construct a PUT request."""
        return self.do_request('PUT', path, data, content_type, **extra)

    def patch(self, path, data=None, content_type=CONTENT_TYPE_APPLICATION_JSON, **extra):
        """Construct a PATCH request."""
        return self.do_request('PATCH', path, data, content_type, **extra)

    def post(self, path, data=None, content_type=CONTENT_TYPE_APPLICATION_JSON, **extra):
        """Construct a PATCH request."""
        return self.do_request('POST', path, data, content_type, **extra)

    def delete(self, path, data=None, content_type=CONTENT_TYPE_APPLICATION_JSON, **extra):
        """Construct a DELETE request."""
        return self.do_request('DELETE', path, data, content_type, **extra)

    def encode_data(self, http_method, path, data, content_type, **extra):
        patch_data = self._encode_data(data, content_type)

        parsed = urlparse(path)
        request = {
            'CONTENT_LENGTH': len(patch_data),
            'CONTENT_TYPE': content_type,
            'PATH_INFO': self._get_path(parsed),
            'QUERY_STRING': parsed[4],
            'REQUEST_METHOD': http_method,
            'wsgi.input': FakePayload(patch_data),
        }
        request.update(extra)

        return request


class BaseTestMixin(object):
    def setUp(self):
        # Flushing all redis databases
        redis.Redis(connection_pool=RedisPools.JOB_CONTAINERS).flushall()
        redis.Redis(connection_pool=RedisPools.TO_STREAM).flushall()
        # Mock dirs
        settings.REPOS_ROOT = tempfile.mkdtemp()
        settings.UPLOAD_ROOT = tempfile.mkdtemp()
        settings.LOGS_ROOT = tempfile.mkdtemp()
        settings.OUTPUTS_ROOT = tempfile.mkdtemp()
        # Flush cache
        cache.clear()
        return super().setUp()


class BaseTest(BaseTestMixin, TestCase):
    pass


class BaseTransactionTest(BaseTestMixin, TransactionTestCase):
    def _fixture_teardown(self):
        # Override SimpleTestCase._fixture_teardown, force TRUNCATE ... CASCADE
        for db_name in self._databases_names(include_mirrors=False):
            # Flush the database
            inhibit_post_migrate = (
                self.available_apps is not None or
                (   # Inhibit the post_migrate signal when using serialized
                    # rollback to avoid trying to recreate the serialized data.
                    self.serialized_rollback and
                    hasattr(connections[db_name], '_test_serialized_contents')
                )
            )
            call_command('flush', verbosity=0, interactive=False,
                         database=db_name, reset_sequences=False,
                         allow_cascade=True,
                         inhibit_post_migrate=inhibit_post_migrate)


class BaseViewTestMixin(object):
    """This is the base test for all tests.

    Also mocks common external calls, e.g. for tracking or related to auth.
    """

    HAS_AUTH = False
    ADMIN_USER = False

    def setUpAuthClient(self):
        if self.ADMIN_USER:
            user = UserFactory(is_staff=True, is_superuser=True)
            self.auth_client = AuthorizedClient(user=user)
        else:
            self.auth_client = AuthorizedClient()

    def setUp(self):
        super().setUp()
        self.setUpAuthClient()

    def test_requires_auth(self):
        # Test unauthorized access to view
        if type(self).HAS_AUTH:
            assert hasattr(self, 'url'), 'Cannot check auth if url is not set.'
            assert self.client.get(self.url).status_code in (status.HTTP_401_UNAUTHORIZED,
                                                             status.HTTP_403_FORBIDDEN)


class BaseViewTest(BaseViewTestMixin, BaseTest):
    pass


class BaseTransactionViewTest(BaseViewTestMixin, BaseTransactionTest):
    pass

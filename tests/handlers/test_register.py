# -*- coding: utf-8 -*-
# Copyright 2015, 2016 OpenMarket Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from twisted.internet import defer
from .. import unittest

from synapse.handlers.register import RegistrationHandler
from synapse.types import UserID

from tests.utils import setup_test_homeserver

from mock import Mock


class RegistrationHandlers(object):
    def __init__(self, hs):
        self.registration_handler = RegistrationHandler(hs)


class RegistrationTestCase(unittest.TestCase):
    """ Tests the RegistrationHandler. """

    @defer.inlineCallbacks
    def setUp(self):
        self.mock_distributor = Mock()
        self.mock_distributor.declare("registered_user")
        self.mock_captcha_client = Mock()
        self.hs = yield setup_test_homeserver(
            handlers=None,
            http_client=None,
            expire_access_token=True)
        self.auth_handler = Mock(
            generate_short_term_login_token=Mock(return_value='secret'))
        self.hs.handlers = RegistrationHandlers(self.hs)
        self.handler = self.hs.get_handlers().registration_handler
        self.hs.get_handlers().profile_handler = Mock()
        self.mock_handler = Mock(spec=[
            "generate_short_term_login_token",
        ])
        self.hs.get_auth_handler = Mock(return_value=self.auth_handler)

    @defer.inlineCallbacks
    def test_user_is_created_and_logged_in_if_doesnt_exist(self):
        duration_ms = 200
        local_part = "someone"
        display_name = "someone"
        user_id = "@someone:test"
        result_user_id, result_token = yield self.handler.get_or_create_user(
            local_part, display_name, duration_ms)
        self.assertEquals(result_user_id, user_id)
        self.assertEquals(result_token, 'secret')

    @defer.inlineCallbacks
    def test_if_user_exists(self):
        store = self.hs.get_datastore()
        frank = UserID.from_string("@frank:test")
        yield store.register(
            user_id=frank.to_string(),
            token="jkv;g498752-43gj['eamb!-5",
            password_hash=None)
        duration_ms = 200
        local_part = "frank"
        display_name = "Frank"
        user_id = "@frank:test"
        result_user_id, result_token = yield self.handler.get_or_create_user(
            local_part, display_name, duration_ms)
        self.assertEquals(result_user_id, user_id)
        self.assertEquals(result_token, 'secret')

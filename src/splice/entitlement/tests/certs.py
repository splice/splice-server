# -*- coding: utf-8 -*-
#
# Copyright © 2012 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
from splice.common import certs, config

# Unit test imports
from base import BaseEntitlementTestCase


class CertsTest(BaseEntitlementTestCase):

    def setUp(self):
        super(CertsTest, self).setUp()

    def tearDown(self):
        super(CertsTest, self).tearDown()

    def test_get_client_cert_from_request(self):
        req = self.request_factory.request(SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        client_cert = certs.get_client_cert_from_request(req)
        self.assertEqual(client_cert, self.valid_identity_cert_pem)

    def test_get_identifier_from_cert(self):
        req = self.request_factory.request(SSL_CLIENT_CERT=self.valid_identity_cert_pem)
        client_cert = certs.get_client_cert_from_request(req)
        CN, O = certs.get_identifier_from_cert(client_cert)
        self.assertEqual(CN, self.expected_valid_identity_uuid)
        self.assertEqual(O, self.expected_valid_account_num)

    def test_get_splice_server_identity(self):
        cn = certs.get_splice_server_identity(self.valid_identity_cert_pem)
        self.assertEqual(cn, self.expected_valid_identity_uuid)
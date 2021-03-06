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

import ConfigParser
from datetime import timedelta
from datetime import datetime
from dateutil.tz import tzutc
from StringIO import StringIO
from uuid import uuid4

from splice.common import splice_server_client
from splice.common.config import BadConfigurationException
from splice.common.models import get_now, ProductUsage, SpliceServer, SpliceServerTransferInfo

# Unit test imports
from base import BaseEntitlementTestCase
from splice.managers import upload

class UploadManagerTest(BaseEntitlementTestCase):

    def setUp(self):
        super(UploadManagerTest, self).setUp()
        self.mocked_arg_of_upload_data = None
        def mocked_upload_data(addr, port, url, data, gzip_body=False):
            self.mocked_arg_of_upload_data = data
        self.orig_upload_product_usage_data = splice_server_client.upload_product_usage_data
        self.orig_upload_splice_server_metadata = splice_server_client.upload_splice_server_metadata
        splice_server_client.upload_product_usage_data = mocked_upload_data
        splice_server_client.upload_splice_server_metadata = mocked_upload_data

    def tearDown(self):
        super(UploadManagerTest, self).tearDown()
        splice_server_client.upload_product_usage_data = self.orig_upload_product_usage_data
        splice_server_client.upload_splice_server_metadata = self.orig_upload_splice_server_metadata

    def create_product_usage_data(self, addr, num, save=True):
        retval = []
        for index in range(0, num):
            pu = ProductUsage()
            pu.splice_server = addr
            pu.consumer = "consumer_uuid"
            pu.date = datetime.now(tzutc()) - timedelta(hours=num-index)
            pu.instance_identifier = "instance_identifier"
            pu.allowed_product_info = ["1"]
            pu.unallowed_product_info = ["0"]
            pu.facts = {"tbd":"values"}
            if save:
                pu.save()
            retval.append(pu)
        return retval

    def create_splice_server_metadata(self, num, save=True):
        retval = []
        for index in range(0, num):
            s = SpliceServer()
            s.uuid = str(uuid4())
            s.description = "Description for %s" % (s.uuid)
            s.hostname = "hostname.example.com"
            s.environment = "environment example"
            # s.created & s.modified will be set on pre_save() hook
            if save:
                s.save()
            retval.append(s)
        return retval

    def create_reporting_config_parser(self, servers):
        raw_config_data = """
[reporting]
servers = %s
[tasks]
upload_product_usage_interval_minutes = 720
upload_product_usage_limit_per_call = 5000
""" % (servers)
        parser = ConfigParser.SafeConfigParser()
        parser.readfp(StringIO(raw_config_data))
        return parser

    def test_upload_product_usage_data_with_bad_config(self):
        servers = "255.255.255.255:443:/splice/api/v1/,127.0.0.1:80:/foo/bar/bz,bad_value_missing_end_colon_before_url:80/foo/bar/bz2"
        cfg = self.create_reporting_config_parser(servers)
        caught = False
        try:
            upload.upload_product_usage_data(cfg=cfg)
        except BadConfigurationException, e:
            self.assertEqual(e.msg, "unable to parse "
                                    "'bad_value_missing_end_colon_before_url:80/foo/bar/bz2' for reporting server info, "
                                    "expected in format of address:port:url")
            caught = True
        self.assertTrue(caught)

    def test_upload_product_usage_data(self):
        servers = "255.255.255.255:443:/splice/api/v1/,127.0.0.1:80:/foo/bar/bz,127.0.0.1:80:/foo/bar/bz2"
        called_args = []
        def mocked_process_product_usage_upload(addr, port, url, limit):
            called_args.append((addr, port, url, limit))
        orig_process_product_usage_upload = upload._process_product_usage_upload
        try:
            upload._process_product_usage_upload = mocked_process_product_usage_upload
            upload.upload_product_usage_data(cfg=self.create_reporting_config_parser(servers))
        finally:
            upload._process_product_usage_upload = orig_process_product_usage_upload
        # Check we processed each server from config info as expected
        self.assertEqual(len(called_args), 3)
        for arg in called_args:
            self.assertTrue(arg[0] in ["255.255.255.255", "127.0.0.1",])
            self.assertTrue(arg[1] in [443, 80])
            self.assertTrue(arg[2] in ["/splice/api/v1/", "/foo/bar/bz", "/foo/bar/bz2"])
            self.assertEqual(arg[3], 5000)

    def test_process_product_usage_upload(self):
        addr = "127.0.0.1"
        port = 443
        url = "/example/url"
        limit = 2
        dummy_data = self.create_product_usage_data(addr, 5)
        upload._process_product_usage_upload(addr, port, url, limit)
        # Verify that the expected product usage data was sent
        self.assertEqual(len(self.mocked_arg_of_upload_data), 2)

        # Simulate next invocation
        upload._process_product_usage_upload(addr, port, url, limit)
        self.assertEqual(len(self.mocked_arg_of_upload_data), 2)

        # Simulate next invocation
        upload._process_product_usage_upload(addr, port, url, limit)
        self.assertEqual(len(self.mocked_arg_of_upload_data), 1)

    def test_process_splice_server_metadata_upload(self):
        addr = "127.0.0.1"
        port = 443
        url = "/example/url"
        dummy_data = self.create_splice_server_metadata(5)
        upload._process_splice_server_metadata_upload(addr, port, url)
        # Verify that the expected data was sent
        self.assertEqual(len(self.mocked_arg_of_upload_data), 5)
        #
        # We've sent all data available in previous call
        # Verify next invocation doesn't even call into upload client
        #
        self.mocked_arg_of_upload_data = None
        upload._process_splice_server_metadata_upload(addr, port, url)
        self.assertIsNone(self.mocked_arg_of_upload_data)

    def test_get_product_usage_data(self):
        addr = "rcs.example.com"
        limit = 2
        # Create dummy data
        dummy_data = self.create_product_usage_data(addr, 5)
        self.assertEqual(len(dummy_data), 5)
        found_data = upload._get_product_usage_data(addr, limit)
        self.assertEqual(len(found_data), 2)

    def test_simple_get_product_usage_data(self):
        addr = "rcs.example.com"
        found_data = list(upload._get_splice_server_metadata(addr)) # convert cursor to list
        self.assertEqual(len(found_data), 0)
        # Create dummy data
        dummy_data = self.create_splice_server_metadata(5)
        self.assertEqual(len(dummy_data), 5)
        found_data = list(upload._get_splice_server_metadata(addr)) # convert cursor to list
        self.assertEqual(len(found_data), 5)


    def test_multiple_endpoints(self):
        # Create ProductUsage entry_a
        # Create endpoint_a
        # Run upload and verify entry_a.tracker has endpoint_a in it
        # Create endpoint_b
        # Create ProductUsage entry_b
        # Re-Run upload
        # Verify
        #  endpoint_a receives only entry_b
        #  endpoint_b receives entry_a and entry_b
        # Re-run upload
        # Verify:
        #  endpoint_a & endpoint_b receive nothing new
        pass


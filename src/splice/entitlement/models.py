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

from datetime import datetime
from dateutil.tz import tzutc

from mongoengine import DateTimeField, Document, ListField, ReferenceField, StringField, DictField, IntField, BooleanField
from mongoengine import signals
from rhic_serve.common.fields import IsoDateTimeField
from rhic_serve.rhic_rcs.models import RHIC
from splice.common.utils import sanitize_key_for_mongo





###
# Overview of what functionality will need to be supported:
# 1) A splice-consumer will checkin with us and pass us: identifier + installed engineering products
#    We will need to:
#    - convert engineering products + identifier to marketing products
#    - determine if identifier is allowed to access marketing products
#    - request entitlement certificate for allowed engineering products
#    - record usage of marketing products
# 2) A splice-server will contact us to ask if we know of a consumer identity
#    We will need to:
#    - check our database to determine if consumer identity is known
#      - if known, return the subscription information for the identity
#    - query our parent for the identity information
# 3) A splice-server will contact us to upload their reporting information
#    We will need to:
#    - accept reporting data, aggregate it with our own data and
#      keep track of path of usage through splice servers
# 4) Be able to import consumer identity information from a file based export or other splice-server
#
# Thoughts/Questions
#  - How does a SpliceServer bootstrap itself on initial setup?
#       - Would the top level entity issue a certificate with a splice server UUID
#       on first-initialization certificate is parsed to determine splice-server UUID
#
#       OR
#
#       - Do we go with a more decentralized approach, where we create our own uuid, then propogate this UUID
#       and the parent/child chain information with our reporting data?
#           Question is from the perspective when we are looking at the reporting data, how do we determine where
#           the usage came from.  Do we look at the chain of parent-child-child-...  or do we assume a splice-server
#           UUID is sufficient?
###

class SpliceServer(Document):
    uuid = StringField(required=True, unique=True)
    description = StringField() # Example what datacenter is this deployed to, i.e. us-east-1
    hostname = StringField(required=True)
    environment = StringField(required=True)
   
    meta = {'allow_inheritance': True}

class RHICLookupTask(Document):
    meta = {
        'collection': 'rhic_lookup_task',
    }
    uuid = StringField(required=True, unique=True)
    task_id = StringField()
    initiated = IsoDateTimeField(default=datetime.now(tzutc()))
    modified = IsoDateTimeField(default=datetime.now(tzutc()))
    completed = BooleanField(default=False)
    status_code = IntField()

    def __str__(self):
        return "RHICLookupTask for '%s' initiated @ '%s', modified @ '%s', " \
               "completed = '%s', status_code = '%s', task_id = '%s'" % \
        (self.uuid, self.initiated, self.modified, self.completed, self.status_code, self.task_id)


class IdentitySyncInfo(Document):
    server_hostname = StringField(required=True, unique=True)
    last_sync = IsoDateTimeField(required=True)

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """
        pre_save signal hook.
        """
        # Ensure that the 'server_hostname' has any "." removed so it can be a key in mongo
        document.server_hostname = sanitize_key_for_mongo(document.server_hostname)
    def __str__(self):
        return "IdentitySyncInfo, server_hostname = %s, last_sync = %s" % (self.server_hostname, self.last_sync)


class ConsumerIdentity(RHIC):

    def __str__(self):
        msg = "Consumer Identity '%s' with engineering_ids '%s', " \
              "created_date '%s', modified_date '%s'" %\
              (self.uuid, self.engineering_ids, self.created_date,
                    self.modified_date)
        if self.deleted:
            msg += ", deleted = %s, deleted_date = %s" % (self.deleted, self.deleted_date)
        return msg

class ProductUsage(Document):
    consumer = StringField(required=True)
    #splice_server = ReferenceField(SpliceServer, required=True)
    splice_server = StringField(required=True) # uuid of Splice Server
    instance_identifier = StringField(required=True) # example: MAC Address
    allowed_product_info = ListField(StringField())
    unallowed_product_info = ListField(StringField())
    facts = DictField()
    date = DateTimeField(required=True)
    
    meta = {'allow_inheritance': True}

    def __str__(self):
        return "Consumer '%s' on Splice Server '%s' from instance '%s' "" \
            ""with allowed_products '%s', "" \
            ""unallowed_products %s at '%s'" % \
            (self.consumer, self.splice_server,
            self.instance_identifier, self.allowed_product_info,
            self.unallowed_product_info,
            self.date)


# Signals
signals.pre_save.connect(IdentitySyncInfo.pre_save, sender=IdentitySyncInfo)

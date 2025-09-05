#
# Copyright (c) 2015-2022 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_content_es.scripts module

This module defines a script entry point which can be used to reindex all site contents.
"""

__docformat__ = 'restructuredtext'

import argparse
import sys
import textwrap
from pyramid.paster import bootstrap

from pyams_content_es.utils import index_site


def pyams_index_cmd():
    """Update Elasticsearch index with all contents"""
    usage = f"usage: {sys.argv[0]} config_uri [-i content_type]* [-x content_type]*"
    description = """Update Elasticsearch index with all database contents."""
    parser = argparse.ArgumentParser(usage=usage,
                                     description=textwrap.dedent(description))
    parser.add_argument('-c', '--check', action='store_true',
                        help="If set, only reindex missing documents")
    parser.add_argument('-r', '--root',
                        help="Define path of indexation root")
    parser.add_argument('-i', '--include', action='append',
                        help="Included shared content types; can be 'topic', 'event'... "
                             "You can set this argument several times to specify several "
                             "content types to include into index")
    parser.add_argument('-x', '--exclude', action='append',
                        help="Excluded shared content types; can be 'topic', 'event'... "
                             "You can set this argument several times to specify several "
                             "content types to exclude from index")
    parser.add_argument('-t', '--timeout', type=float, default=10,
                        help="Document indexer timeout, in seconds (default=10)")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Verbose outputs")
    parser.add_argument('config_uri', help="Configuration filename")
    args = parser.parse_args()

    if args.include and args.exclude:
        print("INCLUDE and EXCLUDE arguments can't be used simultaneously!")
        sys.exit(1)

    env = bootstrap(args.config_uri)
    closer = env['closer']
    try:
        index_site(env['request'], cmd_args=args)
    finally:
        closer()

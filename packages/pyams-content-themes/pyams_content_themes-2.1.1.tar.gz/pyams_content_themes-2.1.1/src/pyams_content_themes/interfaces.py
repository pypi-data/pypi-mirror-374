#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS content themes.interfaces module

"""

from pyams_content.skin.interfaces import IPyAMSDefaultLayer


class IPyAMSAlmondLayer(IPyAMSDefaultLayer):
    """PyAMS Almond theme layer interface"""


class IPyAMSDarkGreenLayer(IPyAMSDefaultLayer):
    """PyAMS Dark Green theme layer interface"""

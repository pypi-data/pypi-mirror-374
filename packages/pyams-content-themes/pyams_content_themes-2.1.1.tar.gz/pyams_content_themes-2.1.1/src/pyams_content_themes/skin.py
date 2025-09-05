#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_*** module

"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface

from pyams_content.skin.interfaces import IPyAMSDefaultLayer
from pyams_content_themes.interfaces import IPyAMSAlmondLayer, IPyAMSDarkGreenLayer
from pyams_layer.interfaces import IResources, ISkin
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.registry import utility_config

from pyams_content_themes import _, pyams_almond_theme, pyams_darkgreen_theme, pyams_default_theme


@utility_config(name='PyAMS default skin',
                provides=ISkin)
class PyAMSDefaultSkin:
    """PyAMS default skin"""

    label = _("PyAMS Bootstrap skin")
    layer = IPyAMSDefaultLayer


@adapter_config(required=(Interface, IPyAMSDefaultLayer, Interface),
                provides=IResources)
class PyAMSDefaultSkinResources(ContextRequestViewAdapter):
    """PyAMS default skin resources"""

    resources = (pyams_default_theme,)


@utility_config(name='PyAMS Almond skin',
                provides=ISkin)
class PyAMSAlmondSkin:
    """PyAMS Almond skin"""

    label = _("PyAMS Almond skin")
    layer = IPyAMSAlmondLayer


@adapter_config(required=(Interface, IPyAMSAlmondLayer, Interface),
                provides=IResources)
class PyAMSAlmondSkinResources(ContextRequestViewAdapter):
    """PyAMS Almond skin resources"""

    resources = (pyams_almond_theme,)


@utility_config(name='PyAMS DarkGreen skin',
                provides=ISkin)
class PyAMSDarkGreenSkin:
    """PyAMS DarkGreen skin"""

    label = _("PyAMS DarkGreen skin")
    layer = IPyAMSDarkGreenLayer


@adapter_config(required=(Interface, IPyAMSDarkGreenLayer, Interface),
                provides=IResources)
class PyAMSDarkGreenSkinResources(ContextRequestViewAdapter):
    """PyAMS DarkGreen skin resources"""

    resources = (pyams_darkgreen_theme,)

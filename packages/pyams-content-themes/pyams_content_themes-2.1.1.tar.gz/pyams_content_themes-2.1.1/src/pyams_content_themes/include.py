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

"""PyAMS content themes.include module

This module is used for Pyramid integration
"""

import re

from pyams_content.skin.interfaces import IPyAMSDefaultLayer
from pyams_form.interfaces import DISPLAY_MODE, INPUT_MODE
from pyams_form.interfaces.form import IForm
from pyams_form.interfaces.widget import IObjectWidget, ISingleCheckBoxWidget, IWidget
from pyams_form.template import override_widget_layout, override_widget_template
from pyams_portal.skin.page import PortalContextIndexPage
from pyams_skin.interfaces.widget import ISubmitWidget
from pyams_template.template import override_layout, override_template

__docformat__ = 'restructuredtext'


def include_package(config):
    """Pyramid package include"""

    # add translations
    config.add_translation_dirs('pyams_content_themes:locales')

    try:
        import pyams_zmi  # pylint: disable=import-outside-toplevel,unused-import
    except ImportError:
        config.scan(ignore=[re.compile(r'pyams_content_themes\..*\.zmi\.?.*').search])
    else:
        config.scan()

    # PyAMS custom templates
    override_layout(PortalContextIndexPage,
                    layer=IPyAMSDefaultLayer,
                    template='templates/layout.pt')

    override_template(IForm,
                      layer=IPyAMSDefaultLayer,
                      template='templates/form-layout.pt')

    # Overriden widgets layouts
    override_widget_layout(IWidget,
                           layer=IPyAMSDefaultLayer,
                           template='templates/widget-layout.pt')

    override_widget_layout(IWidget,
                           mode=DISPLAY_MODE,
                           layer=IPyAMSDefaultLayer,
                           template='templates/widget-layout.pt')

    override_widget_layout(ISingleCheckBoxWidget,
                           layer=IPyAMSDefaultLayer,
                           template='templates/checkbox-layout.pt')

    # Overriden widgets templates
    override_widget_template(IObjectWidget,
                             mode=INPUT_MODE,
                             layer=IPyAMSDefaultLayer,
                             template='templates/object-input.pt')

    override_widget_template(ISubmitWidget,
                             mode=INPUT_MODE,
                             layer=IPyAMSDefaultLayer,
                             template='templates/submit-input.pt')

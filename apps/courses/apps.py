# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CoursesConfig(AppConfig):
    name = 'apps.courses'
    verbose_name = _('App Courses')

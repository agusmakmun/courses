# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db.models import (Q, F, Count)
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import (get_object_or_404, redirect)
from django.views.generic import (ListView, DetailView)

from apps.courses.models.course import (Course, Exercise)


class CourseListView(ListView):
    paginate_by = getattr(settings, 'DEFAULT_PAGINATION_NUMBER', 10)
    template_name = 'apps/courses/list.html'
    queryset = Course.objects.published()
    context_object_name = 'courses'


class CourseDetailView(DetailView):
    template_name = 'apps/courses/detail.html'
    context_object_name = 'course'
    model = Course

    def get_object(self):
        queries = {'slug': self.kwargs['slug'], 'deleted_at__isnull': True}
        return get_object_or_404(self.model, **queries)

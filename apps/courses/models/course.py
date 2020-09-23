# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.courses.models.base import (TimeStampedModel, CustomManager)
from apps.courses.utils import generate_unique_slug


class Course(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    # cover = models.ImageField(_('Cover'), upload_to='covers/%Y/%m/%d',
    #                           null=True, blank=True)
    overview = models.TextField(_('Overview'))
    description = models.TextField(_('Course Description'), blank=True)

    objects = CustomManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        if not self.pk:
            self.slug = generate_unique_slug(self.__class__, self.title)

        return super().save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)


class Exercise(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(_('Title'), max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    description = models.TextField(_('Description'))

    objects = CustomManager()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-id',)


class Answer(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    answer = models.TextField(_('Answer'), help_text=_('The correct answer'))

    objects = CustomManager()

    def __str__(self):
        return self.answer[:50]

    class Meta:
        ordering = ('-id',)

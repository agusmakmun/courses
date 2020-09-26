# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.courses.models.base import (TimeStampedModel, CustomManager)
from apps.courses.utils import generate_unique_slug


class Course(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=200, unique=True)
    cover = models.ImageField(_('Cover'), upload_to='covers/%Y/%m/%d',
                              null=True, blank=True)
    overview = models.TextField(_('Overview'))
    description = models.TextField(_('Course Description'), blank=True)

    objects = CustomManager()

    def get_exercises(self):
        if hasattr(self, 'exercise_set'):
            return self.exercise_set.published().order_by('order')
        return self.__class__.objects.none()

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
    order = models.PositiveIntegerField(_('Order'), default=1)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    sort_description = models.TextField(_('Sort Description'))
    long_description = models.TextField(_('Long Description'))
    initial_script = models.TextField(_('Initial Script'), blank=True)

    validate_script = models.BooleanField(_('Validate Script?'), default=True)
    validate_output = models.BooleanField(_('Validate Output?'), default=False)
    run_expected_script = models.BooleanField(_('Run Expected Script?'), default=False)

    objects = CustomManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        args = [self.course.slug, self.id]
        return reverse('apps.courses:exercise_detail', args=args)

    def get_related_exercises(self):
        return self.__class__.objects.published()\
                                     .filter(course=self.course)

    def get_prev_exercise(self):
        """ function to get the previous exercise by order """
        return self.get_related_exercises()\
                   .filter(order__lt=self.order)\
                   .order_by('-order')\
                   .first()

    def get_next_exercise(self):
        """ function to get the next exercise by order """
        return self.get_related_exercises()\
                   .filter(order__gt=self.order)\
                   .order_by('-order')\
                   .first()

    class Meta:
        ordering = ('-id',)


class ExpectedAnswer(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    expected_script = models.TextField(_('Expected Script'), blank=True)
    expected_output = models.TextField(_('Expected Output'), blank=True)

    objects = CustomManager()

    def __str__(self):
        if self.expected_script:
            return self.expected_script[:50]
        elif self.expected_output:
            return self.expected_output[:50]
        return _('Expected output for %(exercise)s') % {'exercise': self.exercise}

    class Meta:
        ordering = ('-id',)

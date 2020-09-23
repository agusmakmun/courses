# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType


class TimeStampedModel(models.Model):
    """
    TimeStampedModel
    An abstract base class model that provides self-managed
    "created_at", "updated_at" and "deleted_at" fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class CustomManager(models.Manager):
    """
    Class to assign as ORM queryset manager,
    usage example:

    class ModelName(models.Model):
        ...
        objects = CustomManager()
    >>> ModelName.objects.published()
    >>> ModelName.objects.deleted()
    """

    def published(self):
        """ return queryset for not-deleted objects only. """
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        """ return queryset for deleted objects only. """
        return self.filter(deleted_at__isnull=False)

    def get_or_none(self, **kwargs):
        """ function to get the object or None. """
        try:
            return self.get(**kwargs)
        except (Exception, self.model.DoesNotExist):
            return None

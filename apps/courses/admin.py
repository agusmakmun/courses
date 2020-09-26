# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import admin

from martor.widgets import AdminMartorWidget
from apps.courses.models.course import (Course, Exercise, ExpectedAnswer)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')
    prepopulated_fields = {'slug': ['title']}


class ExpectedAnswerInline(admin.TabularInline):
    model = ExpectedAnswer
    extra = 1

    class Media:
        js = ('admin/js/custom_admin.js',)


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')
    inlines = [ExpectedAnswerInline, ]
    formfield_overrides = {
        models.TextField: {'widget': AdminMartorWidget},
    }


class ExpectedAnswerAdmin(admin.ModelAdmin):
    list_display = ('exercise', '__str__', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')


admin.site.register(Course, CourseAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(ExpectedAnswer, ExpectedAnswerAdmin)

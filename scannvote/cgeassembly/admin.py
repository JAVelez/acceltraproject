from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.admin.options import get_content_type_for_model
from django.db import models
from django.contrib import admin

from .models import Assembly, Interaction, Motion, Amendment
import base.models as base


class AssemblyAdmin(admin.ModelAdmin):
    """
        admin model that allows administrator to create, edit and use assemblies
        :param list_display: determines what parameters will be displayed in the screen
        :param list_filter: determines what parameters will filter the display
        :param actions: list of actions that will be available to the administrator
    """
    list_display = ['assembly_name', 'event_date', 'quorum']
    list_filter = ['archived']
    actions = ['make_assembly_archived', 'make_assembly_unArchived', 'make_current', 'turn_off']
    fields = ['assembly_name', 'event_date', 'agenda']

    def log_addition(self, *args):
        """
            method to remove adding action to recent actions display
        """
        return

    def log_change(self, *args):
        """
            method eliminate change actions from recent actions display
        """
        return

    def log_deletion(self, *args):
        """
            method eliminate delete actions from recent actions display
        """
        return

    def make_assembly_archived(self, request, queryset):
        """
            method to archive selected assembly
        """
        queryset.update(archived=True)
    make_assembly_archived.short_description = "Archive selected assembly(s)"

    def make_assembly_unArchived(self, request, queryset):
        """
            method to unArchive selected assembly
        """
        queryset.update(archived=False)
    make_assembly_unArchived.short_description = "Unarchive selected assembly(s)"

    def turn_off(self, request, queryset):
        """
            method to terminate and archive all components of an assembly
        """
        queryset.update(archived=True)

        queryset1 = base.Student.objects.all()
        queryset1.update(attending=False)

        queryset3 = Motion.objects.all()
        queryset3.update(voteable=False)
        queryset3.update(archived=True)

        queryset4 = Amendment.objects.all()
        queryset4.update(archived=True)
    turn_off.short_description = "Conclude assembly"


class MotionAdmin(admin.ModelAdmin):
    """
         admin model that allows administrator to create and edit motions
         :param fieldsets: determines the fields that needs to be filled in the creation or edit of a motion
         :param list_display: determines what parameters will be displayed in the screen
         :param list_filter: determines what parameters will filter the display
         :param actions: list of actions that will be available to the administrator
     """
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_text', ]}),
    ]
    # changelistview
    list_display = ['motion_text', 'is_Amendment', 'assembly', 'a_favor', 'en_contra', 'abstenido',]
    list_filter = ['assembly', 'archived', 'is_Amendment']
    actions = ['make_motion_archived', 'make_motion_votable', 'make_motion_unArchived', 'make_motion_unVotable', 'amend_motion']

    def formfield_for_dbfield(self, *args, **kwargs):
        """
            removes widgets add, change and delete from foreign keys during creation of class object
        """
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_add_related = False
        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False

        return formfield

    def log_addition(self, request, object, message):
        """
            method to add adding action to recent actions display
        """
        messages = "Created motion: %s; for assembly: %s" % (str(object), str(object.assembly))
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=messages,
            action_flag=ADDITION,
            change_message=message)

    def log_change(self, *args):
        """
            method eliminate change actions from recent actions display
        """
        return

    def log_deletion(self, *args):
        """
            method eliminate delete actions from recent actions display
        """
        return

    def make_motion_archived(self, request, queryset):
        """
            method archive motion
        """
        queryset.update(archived=True)
    make_motion_archived.short_description = "Archive selected motion(s)"

    def make_motion_unArchived(self, request, queryset):
        """
            method to unArchive motion
        """
        queryset.update(archived=False)

    make_motion_unArchived.short_description = "Unarchive selected motion(s)"

    def make_motion_votable(self, request, queryset):
        """
            method to make motion votable
        """
        queryset.update(voteable=True)
    make_motion_votable.short_description = "Allow motion to be votable"

    def make_motion_unVotable(self, request, queryset):
        """
            method to make motion not votable
        """
        queryset.update(voteable=False)
    make_motion_unVotable.short_description = "Unallow motion to be votable"

    def amend_motion(self, request, queryset):
        """
            method to make motion not votable
        """
        amended_text = 'Enmendado: ' + Amendment.objects.all().order_by('-date')[0].motion_text + '\nMoción original: ' + queryset[0].motion_text
        queryset.update(motion_text=amended_text)
    amend_motion.short_description = "Amend motion with lastest amendment"


class AmendmentAdmin(admin.ModelAdmin):
    """
        admin model that allows administrator to create and edit amendments
        :param fieldsets: determines the fields that needs to be filled in the creation or edit of an amendment
        :param list_display: determines what parameters will be displayed in the screen
        :param list_filter: determines what parameters will filter the display
        :param actions: list of actions that will be available to the administrator
    """
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_amended', 'motion_text', ]}),
    ]
    # changelistview
    list_display = ['motion_text', 'date', 'assembly']
    list_filter = ['archived']
    actions = ['make_amendment_archived', 'make_amendment_unArchived', 'make_amendment_votable',
               'make_amendment_unVotable', 'amend_amendment']

    def formfield_for_dbfield(self, *args, **kwargs):
        """
            removes widgets add, change and delete from foreign keys during creation of class object
        """
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_add_related = False
        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False

        return formfield

    def log_addition(self, request, object, message):
        """
            method to add adding action to recent actions display
        """
        messages = "Amended motion: %s; with: %s" % (str(object.motion_amended), str(object))
        return LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=messages,  # (str(object),
            action_flag=ADDITION,
            change_message=message)

    def log_change(self, *args):
        """
            method eliminate change actions from recent actions display
        """
        return

    def log_deletion(self, *args):
        """
            method eliminate delete actions from recent actions display
        """
        return

    def make_amendment_archived(self, request, queryset):
        """
            method to make selected amendment an archive amendment
        """
        queryset.update(archived=True)
    make_amendment_archived.short_description = "Archive selected amendment(s)"

    def make_amendment_unArchived(self, request, queryset):
        """
            method to make selected amendment unarchived
        """
        queryset.update(archived=False)

    make_amendment_unArchived.short_description = "Unarchive selected amendment(s)"

    def make_amendment_votable(self, request, queryset):
        """
            method to make amendment votable
        """
        queryset.update(voteable=True)
    make_amendment_votable.short_description = "Allow amendment to be votable"

    def make_amendment_unVotable(self, request, queryset):
        """
            method to make amendment not votable
        """
        queryset.update(voteable=False)
    make_amendment_unVotable.short_description = "Unallow amendment to be votable"

    def amend_amendment(self, request, queryset):
        """
            method to make motion not votable
        """
        amended_text = 'Enmendado: ' + Amendment.objects.all().order_by('-date')[0].motion_text + '\nEnmienda original: ' + queryset[0].motion_text
        queryset.update(motion_text=amended_text)
    amend_amendment.short_description = "Amend amendment with lastest amendment"


admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Amendment, AmendmentAdmin)

from django.contrib import admin

from huscy.subject_notes.models import SubjectNote, SubjectNoteTag
from huscy.subject_notes.services import create_subject_note


class SubjectNoteAdmin(admin.ModelAdmin):

    date_hierarchy = 'created_at'
    fields = 'subject', 'note_tag', 'text', 'creator', 'created_at'
    list_display = 'subject', 'note_tag', 'text', 'creator', 'created_at'
    list_filter = 'note_tag',
    readonly_fields = 'creator', 'created_at'
    search_fields = 'subject__contact__display_name', 'subject__id'

    def save_model(self, request, note, form, change):
        create_subject_note(note.subject, request.user, note.note_tag, note.text)


admin.site.register(SubjectNote, SubjectNoteAdmin)
admin.site.register(SubjectNoteTag)

from rest_framework.permissions import BasePermission


class SubjectNotePermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.has_perm('subjects.change_subject'):
            return True

        if request.method == 'POST':
            return request.user.has_perm('subject_notes.add_subjectnote')

        return False

    def has_object_permission(self, request, view, subject_note):
        if request.method == 'DELETE':
            if request.user.has_perm('subjects.change_subject'):
                return (request.user.has_perm('subject_notes.delete_subjectnote') or
                        request.user.has_perm('subject_notes.delete_subjectnote', subject_note))
        return True

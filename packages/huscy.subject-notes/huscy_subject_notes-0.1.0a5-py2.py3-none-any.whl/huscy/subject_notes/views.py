from django.shortcuts import get_object_or_404
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from huscy.subject_notes import services, serializer
from huscy.subject_notes.permissions import SubjectNotePermission
from huscy.subjects.models import Subject


class SubjectNoteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    permission_classes = IsAuthenticated, SubjectNotePermission
    serializer_class = serializer.SubjectNoteSerializer

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.subject = get_object_or_404(Subject, pk=self.kwargs['subject_pk'])

    def get_queryset(self):
        return services.get_subject_notes(self.subject)

    def perform_create(self, serializer):
        self.object = serializer.save(subject=self.subject)


class SubjectNoteTagViewSet(ModelViewSet):
    permission_classes = IsAuthenticated, DjangoModelPermissions
    serializer_class = serializer.SubjectNoteTagSerializer

    def get_queryset(self):
        return services.get_subject_note_tags()

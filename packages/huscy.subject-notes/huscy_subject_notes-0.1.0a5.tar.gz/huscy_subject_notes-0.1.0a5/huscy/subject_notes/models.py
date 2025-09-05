from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.subjects.models import Subject


class SubjectNoteTag(models.Model):
    text = models.CharField(_('Text'), max_length=255)

    def __str__(self):
        return self.text

    class Meta:
        ordering = 'text',
        verbose_name = _('Subject note tag')
        verbose_name_plural = _('Subject note tags')


class SubjectNote(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='notes',
                                verbose_name=_('Subject'))

    note_tag = models.ForeignKey(SubjectNoteTag, on_delete=models.PROTECT, related_name='+',
                                 verbose_name=_('Subject note tag'))
    text = models.TextField(_('Text'), blank=True)

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                verbose_name=_('Creator'))
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        ordering = 'subject__contact__display_name', '-created_at'
        verbose_name = _('Subject note')
        verbose_name_plural = _('Subject notes')

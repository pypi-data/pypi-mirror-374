from guardian.shortcuts import assign_perm

from huscy.subject_notes.models import SubjectNote, SubjectNoteTag


def create_subject_note(subject, creator, note_tag, text=''):
    args = dict(subject=subject, creator=creator, note_tag=note_tag)
    if note_tag.text.lower() == 'other':
        args.setdefault('text', text)

    note = SubjectNote.objects.create(**args)
    assign_perm('subject_notes.delete_subjectnote', creator, note)

    return note


def create_subject_note_tag(text):
    return SubjectNoteTag.objects.create(text=text)


def get_subject_notes(subject):
    return SubjectNote.objects.filter(subject=subject)


def get_subject_note_tags():
    return SubjectNoteTag.objects.all()

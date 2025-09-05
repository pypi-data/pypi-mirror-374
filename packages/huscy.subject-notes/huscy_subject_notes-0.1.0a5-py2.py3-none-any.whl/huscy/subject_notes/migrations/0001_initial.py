import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('subjects', '0015_alter_subject_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubjectNoteTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255, verbose_name='Text')),
            ],
            options={
                'verbose_name': 'Subject note tag',
                'verbose_name_plural': 'Subject note tags',
                'ordering': ('text',),
            },
        ),
        migrations.CreateModel(
            name='SubjectNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, verbose_name='Text')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Creator')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='subjects.subject', verbose_name='Subject')),
                ('note_tag', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='subject_notes.subjectnotetag', verbose_name='Subject note tag')),
            ],
            options={
                'verbose_name': 'Subject note',
                'verbose_name_plural': 'Subject notes',
                'ordering': ('subject__contact__display_name', '-created_at'),
            },
        ),
    ]

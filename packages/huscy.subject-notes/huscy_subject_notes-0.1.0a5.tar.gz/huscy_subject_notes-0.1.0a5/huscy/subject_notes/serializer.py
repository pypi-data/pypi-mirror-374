from rest_framework import serializers

from huscy.subject_notes import models, services


class SubjectNoteSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_username = serializers.CharField(source='creator.username', read_only=True)

    class Meta:
        model = models.SubjectNote
        fields = (
            'id',
            'created_at',
            'creator',
            'creator_username',
            'note_tag',
            'text',
        )

    def create(self, validated_data):
        return services.create_subject_note(**validated_data)


class SubjectNoteTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.SubjectNoteTag
        fields = (
            'id',
            'text',
        )

    def create(self, validated_data):
        return services.create_subject_note_tag(**validated_data)

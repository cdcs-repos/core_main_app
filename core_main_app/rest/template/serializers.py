"""Serializers used throughout the Rest API
"""
from rest_framework.fields import CharField
from rest_framework_mongoengine.serializers import DocumentSerializer

from core_main_app.components.template.models import Template


class TemplateSerializer(DocumentSerializer):
    """
        Template serializer
    """
    dependencies_dict = CharField(write_only=True, required=False)

    class Meta:
        model = Template
        fields = ['id',
                  'filename',
                  'content',
                  'hash',
                  'dependencies',
                  'dependencies_dict']

        read_only_fields = ['id',
                            'hash',
                            '_display_name', ]

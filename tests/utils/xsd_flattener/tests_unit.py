from unittest import TestCase

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from mock.mock import patch

from core_main_app.commons.exceptions import DoesNotExist
from core_main_app.components.template import api as template_api
from core_main_app.components.template.models import Template
from core_main_app.utils.xsd_flattener.xsd_flattener_database_url import \
    XSDFlattenerDatabaseOrURL, XSDFlattenerURL


class TestXSDFlattenerDatabaseUrl(TestCase):
    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(XSDFlattenerURL, 'get_dependency_content')
    def test_url_not_recognized_use_xsd_flattener_url(self, mock_get_dependency_content):
        # Arrange
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="http://dummy.com/download?id=1234"/></xs:schema>'
        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'
        mock_get_dependency_content.return_value = dependency

        # Act
        flattener = XSDFlattenerDatabaseOrURL(xml_string)
        flat_string = flattener.get_flat()

        # Assert
        self.assertTrue('<xs:element name="test"/>' in flat_string)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(template_api, 'get')
    def test_url_recognized_use_database(self, mock_get):
        # Arrange
        url_template_download = reverse('core_main_app_rest_template_download', kwargs={'pk': 'pk'})
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="http://dummy.com{0}?id=1234"/>' \
                     '</xs:schema>'.format(url_template_download)
        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'
        mock_get.return_value = Template(content=dependency)

        # Act
        flattener = XSDFlattenerDatabaseOrURL(xml_string)
        flat_string = flattener.get_flat()

        # Assert
        self.assertTrue('<xs:element name="test"/>' in flat_string)

    @override_settings(ROOT_URLCONF="core_main_app.urls")
    @patch.object(template_api, 'get')
    @patch.object(XSDFlattenerURL, 'get_dependency_content')
    def test_url_recognized_template_does_not_exist(self, mock_get_dependency_content, mock_get):
        # Arrange
        url_template_download = reverse('core_main_app_rest_template_download', kwargs={'pk': 'pk'})
        xml_string = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:include schemaLocation="http://dummy.com{0}?id=1234"/>' \
                     '</xs:schema>'.format(url_template_download)
        dependency = '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">' \
                     '<xs:element name="test"/></xs:schema>'
        mock_get_dependency_content.return_value = dependency
        mock_get.side_effect = DoesNotExist("Error")

        # Act
        flattener = XSDFlattenerDatabaseOrURL(xml_string)
        flat_string = flattener.get_flat()

        # Assert
        self.assertTrue('<xs:element name="test"/>' in flat_string)

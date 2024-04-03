import os
import unittest
from unittest.mock import patch

from valhalla.common.resolver import resolve, init_str_resolver, init_str_resolver_custom_variables


class TestStringResolver(unittest.TestCase):

    def test_resolve_predefined(self):
        # given:
        init_str_resolver("1.0", "token123")
        init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolve("Testing {VERSION}")

        # then:
        self.assertEqual("Testing 1.0", resolved_string)

    def test_resolve_predefined_version_slug(self):
        # given:
        init_str_resolver("1.0.0", "token123")
        init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolve("some_file_{VERSION_SLUG}.pdf")

        # then:
        self.assertEqual("some_file_1-0-0.pdf", resolved_string)

    def test_resolve_custom_variables(self):
        # given:
        init_str_resolver("1.0", "token123")
        init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolve("Testing {CUSTOM_VAR}")

        # then:
        self.assertEqual("Testing value123", resolved_string)

    @patch.dict(os.environ, {"ENV_VAR": "env_value123"})
    def test_resolve_from_env(self):
        # given:
        init_str_resolver("1.0", "token123")
        init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolve("Testing {ENV_VAR}")

        # then:
        self.assertEqual("Testing env_value123", resolved_string)

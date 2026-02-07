import os
import unittest
from unittest.mock import patch

import valhalla.common.resolver as resolver


class TestStringResolver(unittest.TestCase):
    def test_resolve_no_custom_vars(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_set_version("1.0")
        resolver.init_str_resolver_custom_variables({})

        # when:
        resolved_string = resolver.resolve("Testing {VERSION}")

        # then:
        self.assertEqual("Testing 1.0", resolved_string)

    def test_resolve_predefined(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_set_version("1.0")
        resolver.init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolver.resolve("Testing {VERSION}")
        resolved_string_author = resolver.resolve("Testing {AUTHOR}")

        # then:
        self.assertEqual("Testing 1.0", resolved_string)
        self.assertEqual("Testing kot", resolved_string_author)

    def test_resolve_predefined_version(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_set_version("1.2.14-RC01")
        resolver.init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolver.resolve(
            "Testing {VERSION}; major is {VERSION_MAJOR} and minor is {VERSION_MINOR} and patch {VERSION_PATCH}")

        # then:
        self.assertEqual("Testing 1.2.14-RC01; major is 1 and minor is 2 and patch 14", resolved_string)

    def test_resolve_predefined_version_slug(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_set_version("1.0.0")
        resolver.init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolver.resolve("some_file_{VERSION_SLUG}.pdf")

        # then:
        self.assertEqual("some_file_1-0-0.pdf", resolved_string)

    def test_resolve_custom_variables(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolver.resolve("Testing {CUSTOM_VAR}")

        # then:
        self.assertEqual("Testing value123", resolved_string)

    @patch.dict(os.environ, {"ENV_VAR": "env_value123"})
    def test_resolve_from_env(self):
        # given:
        resolver.init_str_resolver("token123", "kot")
        resolver.init_str_resolver_custom_variables({"CUSTOM_VAR": "value123"})

        # when:
        resolved_string = resolver.resolve("Testing {ENV_VAR}")

        # then:
        self.assertEqual("Testing env_value123", resolved_string)

    def test_resolve_not_initialized_raises_runtime_error(self):
        # given: reset globals (manually because they are persistent in the module)
        resolver.VALHALLA_TOKEN = "not_set"
        
        # when / then:
        with self.assertRaises(RuntimeError) as context:
            resolver.resolve("some string")
        
        self.assertIn("There was no init_str_resolver(...) call", str(context.exception))

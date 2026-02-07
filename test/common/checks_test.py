import unittest
from unittest.mock import MagicMock

from valhalla.common.checks import get_other_release_in_progress


class ChecksTest(unittest.TestCase):

    def test_get_other_release_in_progress_no_other(self):
        # given:
        git_host = MagicMock()
        git_host.get_branches.return_value = ['main', 'release-1.0.0', 'feature-1']
        git_host.get_current_branch.return_value = 'release-1.0.0'

        # when:
        result = get_other_release_in_progress(git_host)

        # then:
        self.assertEqual(result, [])

    def test_get_other_release_in_progress_one_other(self):
        # given:
        git_host = MagicMock()
        git_host.get_branches.return_value = ['main', 'release-1.0.0', 'release-1.1.0']
        git_host.get_current_branch.return_value = 'release-1.1.0'

        # when:
        result = get_other_release_in_progress(git_host)

        # then:
        self.assertEqual(result, ['release-1.0.0'])

    def test_get_other_release_in_progress_multiple_others(self):
        # given:
        git_host = MagicMock()
        git_host.get_branches.return_value = ['main', 'release-1.0.0', 'release-1.1.0', 'release-1.2.0']
        git_host.get_current_branch.return_value = 'release-1.2.0'

        # when:
        result = get_other_release_in_progress(git_host)

        # then:
        self.assertEqual(result, ['release-1.0.0', 'release-1.1.0'])


if __name__ == '__main__':
    unittest.main()

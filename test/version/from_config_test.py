import unittest
from unittest.mock import patch, MagicMock

from valhalla.version.version_to_release import VersionToRelease, ReleaseKind


class _VersionConfig:
    """Stub for VersionConfig used in tests."""
    def __init__(self, from_command=None):
        self.from_command = from_command


class _Cfg:
    """Stub for Config used in tests - uses version_config attribute."""
    def __init__(self, version_config):
        self.version_config = version_config


class VersionFromCommandTest(unittest.TestCase):

    @patch('valhalla.common.executor.Executor.run')
    def test_from_config_executes_command_and_sets_version(self, mock_executor_run):
        # given:
        from valhalla.common.executor import ExecutionResult
        mock_executor_run.return_value = ExecutionResult(0, '1.2.3', '')

        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig('echo 1.2.3')))

        # then:
        self.assertEqual('1.2.3', vtr.version_number_to_release)
        mock_executor_run.assert_called_once_with('echo 1.2.3')

    @patch('valhalla.version.version_to_release.info')
    def test_from_config_skips_when_version_config_is_none(self, mock_info):
        # given:
        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(None))

        # then:
        self.assertEqual('', vtr.version_number_to_release)
        mock_info.assert_called_with("Version is not specified in valhalla.yml, skipping")

    @patch('valhalla.version.version_to_release.info')
    def test_from_config_skips_when_from_command_is_none(self, mock_info):
        # given:
        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig(None)))

        # then:
        self.assertEqual('', vtr.version_number_to_release)
        mock_info.assert_called_with("Version is not specified in valhalla.yml, skipping")

    @patch('valhalla.version.version_to_release.info')
    def test_from_config_skips_when_from_command_is_empty(self, mock_info):
        # given:
        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig('')))

        # then:
        self.assertEqual('', vtr.version_number_to_release)
        mock_info.assert_called_with("Version is not specified in valhalla.yml, skipping")

    @patch('valhalla.version.version_to_release.info')
    def test_from_config_skips_when_from_command_is_whitespace(self, mock_info):
        # given:
        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig('   ')))

        # then:
        self.assertEqual('', vtr.version_number_to_release)
        mock_info.assert_called_with("Version is not specified in valhalla.yml, skipping")

    @patch('valhalla.common.executor.Executor.run')
    def test_from_config_does_not_change_version_when_executor_returns_none(self, mock_executor_run):
        # given:
        mock_executor_run.return_value = None
        vtr = VersionToRelease('original', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig('some-command')))

        # then:
        self.assertEqual('original', vtr.version_number_to_release)
        mock_executor_run.assert_called_once_with('some-command')

    @patch('valhalla.common.executor.Executor.run')
    def test_from_config_overwrites_existing_version(self, mock_executor_run):
        # given:
        from valhalla.common.executor import ExecutionResult
        mock_executor_run.return_value = ExecutionResult(0, '2.0.0', '')

        vtr = VersionToRelease('1.0.0', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg(_VersionConfig('get-version')))

        # then:
        self.assertEqual('2.0.0', vtr.version_number_to_release)

    @patch('valhalla.common.executor.Executor.run')
    def test_from_config_works_with_real_config_class(self, mock_executor_run):
        # given:
        from valhalla.common.executor import ExecutionResult
        from valhalla.common.get_config import Config, VersionConfig, CommitConfig, ReleaseConfig, \
            ReleaseDescriptionConfig, ReleaseAssetsConfig, TagConfig, MergeRequestConfig

        mock_executor_run.return_value = ExecutionResult(0, '3.5.0', '')

        config = Config(
            version_config=VersionConfig('echo 3.5.0'),
            variables={},
            git_host='github',
            commit_before_release=None,
            release_config=ReleaseConfig(ReleaseDescriptionConfig(''), [], None, ReleaseAssetsConfig([], [])),
            tag_config=None,
            commit_after_release=None,
            merge_request=MergeRequestConfig(True, '', '', '', [])
        )

        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(config)

        # then:
        self.assertEqual('3.5.0', vtr.version_number_to_release)
        mock_executor_run.assert_called_once_with('echo 3.5.0')


if __name__ == '__main__':
    unittest.main()

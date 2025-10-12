import unittest
from unittest.mock import patch, MagicMock

from valhalla.version.version_to_release import VersionToRelease, ReleaseKind


class VersionFromCommandTest(unittest.TestCase):

    @patch('subprocess.run')
    def test_from_config_executes_command_and_sets_version(self, mock_run):
        # given:
        proc = MagicMock()
        proc.stdout = '1.2.3'
        proc.stderr = ''
        proc.returncode = 0
        mock_run.return_value = proc

        # Minimal config stub to match the current implementation (expects config.version)
        class _Version:
            def __init__(self, from_command):
                self.from_command = from_command

        class _Cfg:
            def __init__(self, from_command):
                self.version = _Version(from_command)

        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # when:
        vtr.from_config(_Cfg('echo 1.2.3'))

        # then
        self.assertEqual('1.2.3', vtr.version_number_to_release)
        mock_run.assert_called_once()

    @patch('valhalla.version.version_to_release.info')
    def test_from_config_skips_when_no_command(self, mock_info):
        # given:
        class _Cfg:
            def __init__(self, version):
                self.version = version

        vtr = VersionToRelease('', ReleaseKind('valhalla.yml', '', '.'))

        # None version
        vtr.from_config(_Cfg(None))

        # Empty from_command
        class _V:
            def __init__(self, fc=None):
                self.from_command = fc

        # when:
        vtr.from_config(_Cfg(_V(None)))
        v = _V('   ')
        vtr.from_config(_Cfg(v))

        # then:
        self.assertEqual('', vtr.version_number_to_release)
        mock_info.assert_called()


if __name__ == '__main__':
    unittest.main()

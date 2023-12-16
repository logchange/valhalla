import unittest

from valhalla.extends.merge_dicts import merge


class MergeDictsTest(unittest.TestCase):

    def test_merge_dicts(self):
        parent = {
            "commit_before_release": {
                "msg": "ABC Releasing version {VERSION}",
                "before": [
                    "parent element 1",
                    "parent element 2"
                ],
            },
            "merge_request": {
                "title": "parent title",
                "description": "parent description",
            },
        }

        child = {
            "extends": [
                "https://raw.githubusercontent.com/logchange/valhalla/master/valhalla-extends.yml"
            ],
            "git_host": "gitlab",
            "commit_before_release": {
                "enabled": True,
                "username": "Test1234",
                "email": "test-valhalla@logchange.dev",
                "msg": "Releasing version {VERSION}",
                "before": [
                    "child element 1",
                    "child element 2",
                    "child element 3"
                ],
            },
            "release": {
                "description": {
                    "from_command": "cat changelog / v{VERSION} / version_summary.md"
                },
                "assets": {
                    "links": [
                        {
                            "name": "Documentation",
                            "url": "https: // google.com / q?={VERSION}",
                            "link_type": "other",
                        },
                        {
                            "name": "Docker Image",
                            "url": "https://dockerhub.com/q?={VERSION}",
                            "link_type": "image",
                        },
                    ]
                },
            },
            "commit_after_release": {
                "enabled": True,
                "username": "Test1234",
                "email": "test-valhalla@logchange.dev",
                "msg": "Preparation for next development cycle",
                "before": ['echo "test" > prepare_next_iteration.md'],
            },
            "merge_request": {
                "enabled": True,
                "title": "child title",
                "reviewers": ["peter.zmilczak", "some_uknownwnnaa"],
            },
        }

        result = merge(parent, child)

        self.assertEqual(result['extends'],
                         ['https://raw.githubusercontent.com/logchange/valhalla/master/valhalla-extends.yml'])
        self.assertEqual(result['git_host'], 'gitlab')

        self.assertEqual(result['commit_before_release']['before'], [
            "child element 1",
            "child element 2",
            "child element 3"
        ])

        self.assertEqual(result['merge_request']['title'], 'child title')
        self.assertEqual(result['merge_request']['description'], 'parent description')

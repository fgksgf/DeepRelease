import unittest

from entity.pull_request import PullRequest


class TestPullRequest(unittest.TestCase):
    pr = PullRequest('test', 'test')

    def test_init(self):
        self.assertEqual(self.pr.url, 'test')
        self.assertEqual(self.pr.commit, 'test')
        self.assertEqual(self.pr.id, hash('test'))

    def test_set_data(self):
        data = {
            'title': ' test 测试 @test #55 ',
            'bodyText': ' test 测试\n @test test@test.com ### ',
            'commits': {
                'nodes': [
                    {
                        'commit': {
                            'messages': ' test 测试\n @test test@test.com ### ',
                        },
                    }
                ]
            }
        }
        self.pr.set_data(data)
        self.assertEqual(['test'], self.pr.title)
        self.assertEqual(['test', '.'], self.pr.description)
        self.assertEqual(['test', '.'], self.pr.commit_messages)

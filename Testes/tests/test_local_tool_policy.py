import unittest
from local_tool_policy import available_local_tools

class LocalToolPolicyTests(unittest.TestCase):
    def setUp(self):
        self.schema=[{'function':{'name':'open_app'}}, {'function':{'name':'open_url'}}, {'function':{'name':'search_web'}}, {'function':{'name':'research_web'}}, {'function':{'name':'search_files'}}]
    def test_external_tools_off_by_default(self):
        result=available_local_tools(self.schema, research_enabled=False, browser_enabled=False)
        self.assertEqual([x['function']['name'] for x in result], ['open_app','search_files'])
    def test_explicit_research_permission(self):
        result=available_local_tools(self.schema, research_enabled=True, browser_enabled=False)
        self.assertIn('research_web', [x['function']['name'] for x in result])
        self.assertNotIn('open_url', [x['function']['name'] for x in result])
    def test_explicit_browser_permission(self):
        result=available_local_tools(self.schema, research_enabled=False, browser_enabled=True)
        names=[x['function']['name'] for x in result]
        self.assertIn('open_url', names)
        self.assertIn('search_web', names)
        self.assertNotIn('research_web', names)
if __name__ == '__main__': unittest.main()

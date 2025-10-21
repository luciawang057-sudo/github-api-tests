
import pytest
class TestDeleteRulesetSmoke:
    def test_delete_ruleset_smoke(self,github_client,factory_fixture_with_delete_ruleset):
        ruleset_id=factory_fixture_with_delete_ruleset()
        delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}')
        assert  delete_response.status_code == 204

        with pytest.raises(Exception) as e:
            assert hasattr(e.value,'response')
            assert e.value.response.status_code==404
            print('ruleset已经被删除')

class TestDeleteRulesetConflict:
    def test_delete_ruleset_with_wrong_id(self, github_client,factory_fixture_with_delete_ruleset):
        wrong_ruleset_id=999999999999
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{wrong_ruleset_id}')
            assert hasattr(e.value, 'response')
            assert e.value.response.status_code == 404
            print('ruleset已经被删除')

    def test_delete_ruleset_repeated(self, github_client,factory_fixture_with_delete_ruleset):
        ruleset_id=factory_fixture_with_delete_ruleset()
        delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}')
        assert delete_response.status_code == 204

        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}')
            assert hasattr(e.value, 'response')
            assert e.value.response.status_code == 404
            print('无法重复删除')

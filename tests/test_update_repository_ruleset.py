
import pytest
import random
#删除和更新的必要的创建环节，可以用fixture替代

def assert_update_repository_ruleset_success(response,json,expected_code=200):
    correct_code =response.status_code
    assert correct_code==expected_code

    try:
        correct_data = response.json()
    except ValueError:
        raise AssertionError("响应体不是有效的JSON格式")


    assert isinstance(correct_data,dict)
    print(f'响应体信息：{correct_data}')
    print(f'响应码：{correct_code}')
    filed=[('id',int),('name',str),('target',str),('enforcement',str),( 'source_type',str),('source',str),('node_id',str)]
    for key,expected_type in filed:
        assert key in correct_data
        assert isinstance(correct_data[key],expected_type)
    return correct_data


class TestUpdateRepositoryRulesetSmoke:
    def test_update_repository_ruleset_smoke(self,github_client,factory_fixture_with_update_ruleset):
        ruleset_id = factory_fixture_with_update_ruleset(
            target='branch',enforcement='active'
        )

        update_data={
            'name':'updated-name-smoke-test',
            'target':'tag',
            'enforcement':'disabled',

        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=update_data)

        correct_data=assert_update_repository_ruleset_success(response,update_data,expected_code=200)
        assert correct_data['target'] == update_data['target']
        assert correct_data['enforcement'] == update_data['enforcement']
        assert correct_data['name'] == update_data['name']

class TestUpdateRepositoryRulesetSuccess:
    @pytest.mark.parametrize('target,enforcement',[
        ('branch', 'disabled'),
        ('branch', 'disabled'),
        ('tag', 'active'),
        ('tag', 'disabled'),

        ]
    )
    def test_update_repository_ruleset_success_by_target_enforcement(self,github_client,factory_fixture_with_update_ruleset,target,enforcement):
        ruleset_id = factory_fixture_with_update_ruleset()

        update_json={
            'target':target,
            'enforcement':enforcement
        }
        response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=update_json)
        response_data=assert_update_repository_ruleset_success(response,update_json,expected_code=200)
        print(f'更新后的响应体：{response_data}')
        assert response_data['id'] == ruleset_id
        assert response_data['target'] == update_json['target']
        assert response_data['enforcement'] == update_json['enforcement']

    def test_update_repository_ruleset_success_by_condition(self,github_client,factory_fixture_with_update_ruleset):
        condition_json={#传入的是value值，根据工厂函数
                'ref_name':{
                    'include':['~ALL'],
                    'exclude':['~DEFAULT_BRANCH']
            }

        }
        ruleset_id = factory_fixture_with_update_ruleset(conditions=condition_json)
        update_condition_json={
            'conditions':{
                'ref_name':{
                    'include':['~DEFAULT_BRANCH'],
                    'exclude':[]
            }
        }
        }
        response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=update_condition_json)
        response_data=assert_update_repository_ruleset_success(response,update_condition_json, expected_code=200)
        print(f'更新后的响应体：{response_data}')
        assert response_data['conditions']['ref_name']['include'] == update_condition_json['conditions']['ref_name']['include']
        assert response_data['conditions']['ref_name']['exclude'] == update_condition_json['conditions']['ref_name']['exclude']

    def test_update_repository_ruleset_success_by_rules(self,github_client,factory_fixture_with_update_ruleset):
        rules=[{'type':'required_signatures'},{'type':'non_fast_forward'}]
        ruleset_id=factory_fixture_with_update_ruleset(rules=rules)
        update_rules=[ {'type':'creation'},{'type':'deletion'},{'type':'update'}]
        update_json={
            'rules':update_rules
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=update_json)
        response_data=assert_update_repository_ruleset_success(response,update_json,expected_code=200)
        print(f'更新后的响应体：{response_data}')
        assert response_data['rules']==update_json['rules']

    def test_update_repository_ruleset_success_by_bybypass_actors(self,github_client,factory_fixture_with_update_ruleset):
        ruleset_id=factory_fixture_with_update_ruleset()
        update_json={
            'bypass_actors':[]
        }
        response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=update_json)
        response_data=assert_update_repository_ruleset_success(response,update_json,expected_code=200)
        print(f'更新后的响应体：{response_data}')
        assert response_data['bypass_actors'] == update_json['bypass_actors']
    def test_update_repository_ruleset_with_wrong_ruleset_id(self,github_client,factory_fixture_with_update_ruleset):
        ruleset_id=99999999
        json_data={
            'target': 'branch',
            'enforcement':'active'
        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=json_data)
        assert isinstance(e.value,Exception)
        error_data=e.value.response.json()
        print(f'错误信息{error_data}')
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == '404'

    def test_update_repository_ruleset_with_all_parameters(self,github_client,factory_fixture_with_update_ruleset):

        ruleset_id = factory_fixture_with_update_ruleset(
            name=f'test_{random.randint(100,1000)}',
            target='branch',
            enforcement='active',
            conditions={
                 'ref_name': {
                    'include': ['~DEFAULT_BRANCH'],
                    'exclude': ['refs/heads/tests']
                    }},
             rules=[{'type':'creation'}]
                                                         )
        updated_json_data={
            'name':f'test_{random.randint(1,100)}',
            'target':'tag',
            'enforcement':'disabled',
            'conditions':{
                'ref_name':{
                    'include':['~ALL'],
                    'exclude':[]
                }
            },
            'bypass_actors': [],
            'rules':[{'type':'update'},{'type': 'creation'}]
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}',json=updated_json_data)
        response_data=assert_update_repository_ruleset_success(response,updated_json_data,expected_code=200)
        print(f'更新后的响应体：{response_data}')
        fields =['name','target','enforcement','conditions','bypass_actors']
        for field in fields:
            assert response_data[field] == updated_json_data[field],f"字段 {field} 内容"
        assert len(response_data['rules']) ==len(updated_json_data['rules'])



        # assert response_data['bypass_actors'] ==updated_json_data['bypass_actors']
        # assert response_data['conditions']['ref_name']['include'] == updated_json_data['conditions']['ref_name']['include']
        # assert response_data['conditions']['ref_name']['exclude'] == updated_json_data['conditions']['ref_name']['exclude']
        # assert response_data['target'] == updated_json_data['target']
        # assert response_data['enforcement'] == updated_json_data['enforcement']
        # assert response_data['name'] == updated_json_data['name']





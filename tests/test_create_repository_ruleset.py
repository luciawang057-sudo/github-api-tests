
import pytest
import random


def assert_created_ruleset(response, json, auto_clean_ruleset=None):
    assert response.status_code == 201
    response_data = response.json()
    print(f'返回响应体:{response_data}')
    assert isinstance(response_data, dict)
    assert response_data.get('name') == json['name']
    assert response_data.get('target') == json.get('target')
    assert response_data.get('enforcement') == json.get('enforcement')
    if auto_clean_ruleset is not None:
        ruleset_id = response_data['id']
        auto_clean_ruleset.append(ruleset_id)
        print(f'创建成功，ID: {ruleset_id}')
    return response_data

class TestCreateRepositoryRulesetSmoke:


    def test_create_repository_ruleset_smoke(self,github_client,auto_clean_ruleset):
        json={
            'name':f'test-ruleset{random.randint(1000,9999)}',
            'target':'branch',
            'enforcement':'active'
        }
        response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets',json=json)
        assert_created_ruleset(response, json, auto_clean_ruleset)





class TestCreateRepositoryRulesetSuccess:
    @pytest.mark.parametrize('target,enforcement',[
        ('branch', 'active'),
        ('branch', 'disabled'),
        ('tag', 'active'),
        ('tag', 'disabled'),



    ])
    def test_create_repository_ruleset_success(self, github_client,auto_clean_ruleset,target,enforcement):
        json={
            'name':f'test-ruleset{random.randint(1000,9999)}',
            'target':target,
            'enforcement':enforcement

        }

        response=github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets',json=json)
        assert_created_ruleset(response, json, auto_clean_ruleset)


class TestByPassActors:
    @pytest.mark.parametrize('actor_id,actor_type,bypass_mode',[
        (1,'Integration','always'),
        (1,'OrganizationAdmin','always'),
        (1,'RepositoryRole','always'),
        (1,'Team','always'),
        (1,'DeployKey','always'),
        (None,'Integration','always'),
        (None,'OrganizationAdmin','always'),
        (None,'RepositoryRole','always'),
        (None,'Team','always'),
        (None,'DeployKey','always'),
        (None,'DeployKey','pull_request')

    ])
    def test_bypass_actors(self,github_client,actor_id,actor_type,bypass_mode,auto_clean_ruleset):
        json = {
            'name':f'test-ruleset{random.randint(1000,9999)}',
            'target':'branch',
            'enforcement':'active',
                          'bypass_actors':[
            {
                'actor_id': actor_id,
                'actor_type': actor_type,
                'bypass_mode': bypass_mode
            }]
        }
        try:
            response = github_client.post('/repo/luciawang057-sudo/github-api-tests/rulesets',json=json)
            if response.status_code == 201:
                response_data = response.json()
                ruleset_id = response_data['id']
                auto_clean_ruleset.append(ruleset_id)
                print(f'创建成功，actor_id是{actor_id},actor_type是{actor_type}，bypass_mode是{bypass_mode}，符合预期')
            else:
                error_data = response.json()
                print(f'创建失败，actor_id是{actor_id},actor_type是{actor_type}，bypass_mode是{bypass_mode}，创建失败')
                print(f'错误信息：{error_data}')
        except Exception as e:
            if hasattr(e,'response'):
                error_data = e.response.json()
                print(f'创建失败，actor_id是{actor_id},actor_type是{actor_type}，bypass_mode是{bypass_mode}，出现异常')
                print(f'异常信息：{error_data}')
            else:
                print(f'💥 {actor_type} + actor_id={actor_id} + {bypass_mode} 异常: {e}')

    def test_bypass_actors_by_empty_array(self,github_client,auto_clean_ruleset):
        json={
            'name':f'test-ruleset{random.randint(1000,9999)}',
            'target':'branch',
            'enforcement':'active',
            'bypass_actors':[]
        }
        try:
            response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
            assert_created_ruleset(response, json, auto_clean_ruleset)
        except Exception as e:
            if hasattr(e,'response'):
                error_data = e.response.json()
                print(f'错误信息：{error_data}')
                print(f'错误响应码：{e.response.status_code}')
                github_client.logger.error(f'记录错误{e}')

class TestRulesetCondition:
    @pytest.mark.parametrize('include,exclude', [
        (['refs/heads/main'],[]),
        (['refs/heads/tests'],[]),
        (['refs/heads/main'],['refs/heads/tests']),
        (['refs/heads/master'],[]),
        ([],['refs/heads/main']),
        ([],['refs/heads/tests']),
        ([],['refs/heads/master']),
        ([], ["~DEFAULT_BRANCH"]),
        (["~DEFAULT_BRANCH"],[]),
        (["~ALL"],[]),
        ([],["~ALL"]),
        (["~DEFAULT_BRANCH"],['refs/heads/tests']),
        (["~ALL"],['refs/heads/tests']),
        (["~DEFAULT_BRANCH"],["~ALL"])
    ]
    )
    def test_conditions_ref_name(self,github_client,include,exclude,auto_clean_ruleset):
        json={
            'name': f'test-ruleset{random.randint(1000, 9999)}',
            'target':'branch',
            'enforcement':'active',
            'conditions': {
                'ref_name': {
                    'include': include,
                    'exclude': exclude
                }
            }
        }
        try:
            response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
            response_data =assert_created_ruleset(response, json, auto_clean_ruleset)

            if 'conditions' in json:
                assert 'conditions' in response_data
                assert 'ref_name' in response_data['conditions']
                assert response_data['conditions']['ref_name']['include'] ==json['conditions']['ref_name']['include']
                assert response_data['conditions']['ref_name']['exclude'] == json['conditions']['ref_name']['exclude']
        except Exception as e:
            if hasattr(e, 'response'):
                error_data = e.response.json()
                print(f'错误信息：{error_data}')
                print(f'错误响应码：{e.response.status_code}')
                github_client.logger.error(f'记录错误{e}')

class TestRulesetRules:
   @pytest.mark.parametrize('rule_type',[
       'creation',
       'update',
       'deletion',
       'required_linear_history',
       'required_signatures',
       'non_fast_forward'
   ])
   def test_parameterless_rules_creation(self, github_client, auto_clean_ruleset, rule_type):
       json = {
                   'name': f'test-ruleset{random.randint(1000, 9999)}',
                   'target':'branch',
                   'enforcement':'active',
                    'rules':[
                        {
                            'type':rule_type
                        }
                    ]
       }
       response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
       response_data = assert_created_ruleset(response, json, auto_clean_ruleset)
       assert 'rules' in response_data
       assert isinstance(response_data['rules'], list)
       assert len(response_data['rules']) == 1#验证我们请求中只创建了1个规则。
       assert response_data['rules'][0]['type']==rule_type


   def test_multiple_parameterless_rules_combination(self,github_client, auto_clean_ruleset):
       json = {
           'name': f'test-ruleset{random.randint(1000, 9999)}',
           'target': 'branch',
           'enforcement': 'active',
           'rules': [

            {'type': 'creation'},
            {'type': 'deletion'},
               {'type':'update'},
            {'type': 'required_linear_history'},
            {'type': 'required_signatures'},
               {'type': 'non_fast_forward'}


           ]
       }
       response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
       response_data = assert_created_ruleset(response, json, auto_clean_ruleset)

       assert 'rules' in response_data
       assert isinstance(response_data['rules'], list)
       assert len(response_data['rules']) == 6#验证我们请求中只创建了1个规则。
       actual_rule_type=[rule['type'] for rule in response_data['rules']]#提取响应中每个type
       # actual_rule_type=[]
       # for rule in response_data['rules']:
       #     actual_rule_type.append(rule['type'])
       expected_rules = ['creation', 'deletion', 'update', 'required_linear_history', 'required_signatures', 'non_fast_forward']
       assert expected_rules == actual_rule_type

class TestCreateRulesetConflictBoundary:
    @pytest.mark.parametrize('name,expected_code', [
        ('a',201),(123,422),('中文',201),('TEST_NAME',201),(None,422),('',422),(' ',422),('React@!',201),('test_name',201),('test_name',201),
        ('a'*100,201),('a'*200,422)
    ]


    )
    def test_Boundary_and_conflict_with_name(self, github_client, auto_clean_ruleset, name, expected_code):
        json = {
            'name': name,
            'target':'branch',
            'enforcement':'active'


        }
        try:
            response=github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets',json=json)
            if expected_code == 201:
                assert response.status_code == expected_code
                assert_created_ruleset(response, json, auto_clean_ruleset)
            else:
                error_data = response.json()
                print(f'错误响应体：{error_data}')
                print(f'错误响应慢：{response.status_code}')
                assert 'message' in error_data

        except Exception as e:
            if hasattr(e,'response'):
                error_data = e.response.json()
                print(f'错误响应体：{error_data}')
                print(f'错误响应慢：{e.response.status_code}')
                assert e.response.status_code == expected_code
                assert 'message' in error_data
                assert  'status' in error_data
                assert error_data['status'] == f'{expected_code}'

    @pytest.mark.parametrize('target,expected_code', [
        ('a', 422), (123, 422), ('中文', 422),  (None, 422), ('', 422), (' ', 422), ('React@!', 422)
    ])
    def test_Boundary_and_conflict_with_target(self, github_client, auto_clean_ruleset, target, expected_code):
        json={
            'name':f'test_{random.randint(1000,9999)}',
            'target': target,
            'enforcement': 'active'
        }

        with pytest.raises(Exception) as e:
            github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
        assert hasattr(e.value,'response')
        error_data = e.value.response.json()
        print(f'错误响应体：{error_data}')
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == f'{expected_code}'

    @pytest.mark.parametrize('enforcement,expected_code', [
        ('a', 422), (123, 422), ('中文', 422), (None, 422), ('', 422), (' ', 422), ('React@!', 422)
    ])
    def test_Boundary_and_conflict_with_enforcement(self, github_client, auto_clean_ruleset, enforcement, expected_code):
        json={
            'name': f'test_{random.randint(1000, 9999)}',
            'target': 'branch',
            'enforcement': enforcement
        }

        with pytest.raises(Exception) as e:
            github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
        assert hasattr(e.value,'response')
        error_data = e.value.response.json()
        print(f'错误响应体：{error_data}')
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == f'{expected_code}'


    @pytest.mark.parametrize('target,enforcement,expected_code', [
        ('branch', 'evaluate',422),
        ('tag','evaluate',422),
        ('push','activate',422),
        ('push','disabled',422),
        ('push','evaluate',422),
        ('pull','activate',422)
        ])
    def test_ruleset_conflict_with_target_and_enforcement(self, github_client, auto_clean_ruleset,target,enforcement,expected_code):
        json={
            'name': f'test_{random.randint(1000, 9999)}',
            'target': target,
            'enforcement': enforcement
        }
        with pytest.raises(Exception) as e:
            github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets', json=json)
        assert hasattr(e.value,'response')
        error_data = e.value.response.json()
        print(f'错误响应体：{error_data}')
        print(f'错误响应码：{e.value.response.status_code}')
        assert e.value.response.status_code == expected_code
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == f'{expected_code}'


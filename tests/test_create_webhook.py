import random
import pytest



def assert_create_success(response,json_data,expected_code=201):
    correct_data = response.json()
    correct_code = response.status_code
    print(f'正确响应体：{correct_data}')
    print(f'正确响应码：{correct_code}')
    assert response.status_code == expected_code
    assert isinstance(correct_data, dict)
    assert 'id' in correct_data
    assert 'config' in correct_data
    assert 'url' in correct_data['config']
    return correct_data  # 需要添加这行

def assert_create_failure(exception,expected_code,json_data=None):
    assert hasattr(exception, 'response')
    error_data = exception.response.json()
    error_code =exception.response.status_code
    print(f'错误响应码：{error_code}')
    print(f'错误响应体：{error_data}')
    assert error_code == expected_code
    assert isinstance(error_data, dict)
    assert 'message' in error_data
    assert 'status' in error_data
    assert error_data['status'] == f'{expected_code}'


class TestCreateWebhookSmoke:
    def test_create_webhook_smoke(self,github_client):
        data={
            'name':'web',
            'config':{
                'url':"https://example.com/webhook",
                'content_type':"json",
                'secret':f"test_secrets_{random.randint(100,999)}",
                'insecure_ssl':'1'
            },
            'events':['push'],
            'active':True
        }
        response=github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks',json=data)
        correct_data=assert_create_success(response,data,expected_code=201)
        hook_id = correct_data['id']
        delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
        assert delete_response.status_code == 204
        print('删除成功')

class TestCreateWebhookSuccess:
    def test_create_success_only_repo_onwer_minimal_body(self,github_client):
        minimal_body = {
            "config": {
                "url": "https://example.com/webhook"
            },
            'events': ['push']
            }
        response=github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks',json=minimal_body)
        correct_data=assert_create_success(response,minimal_body)
        assert correct_data['name'] == 'web'
        assert correct_data['events'] == ['push']
        hook_id = correct_data['id']
        delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
        assert delete_response.status_code == 204

    def test_create_success_with_events(self, github_client):
        body_data = {
            "config": {
                "url": "https://example.com/webhook"
            },
            'events': ['pull_request']
        }
        response=github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks',json=body_data)
        correct_data = assert_create_success(response,body_data)
        assert correct_data['events'] == ['pull_request']
        hook_id = correct_data['id']
        delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
        assert delete_response.status_code == 204
    def test_create_success_with_active(self, github_client):
        body_data = {
            "config": {
                "url": "https://example.com/webhook"
            },
            'active':False
        }
        response=github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks',json=body_data)
        correct_data = assert_create_success(response, body_data)

        assert correct_data['active'] == body_data['active']
        hook_id = correct_data['id']
        delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
        assert delete_response.status_code == 204

class TestCreateWebhookConflict:
    def test_create_webhook_repeated(self,github_client):
        data = {
            'name': 'web',
            'config': {
                'url': "https://example.com/webhook",
                'content_type': "json",
                'secret': f"test_secrets_123",
                'insecure_ssl': '1'
            },
            'events': ['push'],
            'active': True
        }
        first_response=github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks',json=data)
        assert_create_success(first_response,data,expected_code=201)

        with pytest.raises(Exception) as e:
            github_client.post(f'/repos/luciawang057-sudo/github-api-tests/hooks',json=data)
        assert_create_failure(e.value,expected_code=422)

        hook_id = first_response.json()['id']
        delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
        assert delete_response.status_code == 204

    def test_create_webhook_with_403(self,github_client):
        test_repos = [
            'github/roadmap',  # GitHub 官方路线图
            'github/feedback',  # GitHub 反馈仓库
            'microsoft/TypeScript',  # TypeScript
        ]

        data = {
            'name': 'web',
            'config': {
                'url': "https://example.com/webhook",
                'content_type': "json",
                'secret': f"test_secrets_123",
                'insecure_ssl': '1'
            },
            'events': ['push'],
            'active': True
        }
        for repo in test_repos:
           with pytest.raises(Exception) as e:
               github_client.post(f'/repos/{repo}/hooks', json=data)
           assert_create_failure(e.value,expected_code=404)


    @pytest.mark.parametrize('name,events,active,expected_code', [
        #name边界
        ('wyx', ['pull_request'],True,422),
        (123, ['pull_request'], False,422),
        (None, ['pull_request'], False,422),
        ('', ['pull_request'], False,422),
        ('WEB', ['pull_request'], False,422),
        ('w eb', ['pull_request'], True,422),
        (' ', ['pull_request'], False,422),
        #events边界
        ('web',['wyx'], False,422),
        ('web',[ 123], False,422),
        ('web', [None], False,422),
        ('web', ['PUSH'], False,422),
        ('web', ['p ush'], False,422),
        ('web', [''], False,422),
        ('web', [' '], False,422),
        ('web', [], False,201),
        #active边界
        ('web',['push'],None,422),
        ('web',['push'],'',422),
        ('web',['PUSH'], 123,422),
        ('web',['PUSH'], ' ',422),
        ('web',['PUSH'],'TRUE',422)]
                             )




    def test_create_webhook_with_name_events_active_params(self, github_client, name, events, active,expected_code):

        webhook_data = {
            'name':name,
            "config": {
                "url": "https://example.com/webhook"
            },
            'events':events,
            'active':active
        }
        print(f"测试参数: name={name}, events={events}, active={active}")

        if expected_code == 201:
            response=github_client.post(f'/repos/luciawang057-sudo/github-api-tests/hooks',json=webhook_data)
            assert response.status_code == expected_code
            correct_data=assert_create_success(response,webhook_data,expected_code=201)
            assert correct_data['active'] == webhook_data['active']
            assert correct_data['events'] == ['push']#默认值
            assert correct_data['name'] == webhook_data['name']
            assert correct_data['config']['url'] == webhook_data['config']['url']
            hook_id=correct_data['id']
            delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hook_id}')
            assert delete_response.status_code == 204
        else:
            with pytest.raises(Exception) as e:
                    github_client.post(f'/repos/luciawang057-sudo/github-api-tests/hooks',json=webhook_data)
            assert_create_failure(e.value,expected_code=expected_code)


    @pytest.mark.parametrize('url,content_type,secret,insecure_ssl,expected_code', [
        #url边界
        (None,'json','wyx123',1,422),
        ('','json','wyx123',1,422),
        ('https://example.com/   webhook','json','wyx123',1,422),
        ('https://example.com//video/BV1uW411M7Qp/?spm_id_from=333.788.recommend_more_video.-1&trackid=web_related_0.router-related-2206146-n7lrp.1760706687740.573&vd_source=a5b89573f89e0a7b1248a4b644b333ab','json','wyx123',1,422),
        (' ','json','wyx123',1,422),
        ('wyx','json','wyx123',1,422),
        (123,'json','wyx123',1,422),
        #content_type边界
        ('https://example.com/hook','application/json','wyx123',1,422),
        ('https://example.com//hook','txt','wyx123',1,422),
        ('https://example.com//hook',None,'wyx123',1,422),
        ('https://example.com//hook','JSON','wyx123',1,422),
        ('https://example.com//hook','','wyx123',1,422),
        ('https://example.com//hook',' ','wyx123',1,422),
        ('https://example.com//hook','j  son ','wyx123',1,422),
        ('https://example.com//hook',123, 'wyx123', 1,422),
        #secret边界
        ('https://example.com//hook', 'json',123, 1,422),
        ('https://example.com//hook','json',None, 1,422),
        ('https://example.com//hook', 'json','',1,422),
        ('https://example.com//hook', 'json',' ',1,422),
        ('https://example.com//hook', 'json','wyx    123',1,422),
        ('https://example.com//hook', 'json','wyx123'*50,1,422),
        #insecure_ssl边界
        ('https://example.com//hook', 'json','wyx123',2,422),
        ('https://example.com//hook', 'json','wyx123',None,422),
        ('https://example.com//hook', 'txt','wyx123','',422),
        ('https://example.com//hook', 'txt','wyx123',' ',422),
    ])

    def test_create_webhook_with_config_params(self,github_client,url,content_type,secret,insecure_ssl,expected_code):
        webhook_data = {
                'name':f'test_webhook_{random.randint(100,999)}',
                "config": {
                    "url": url,
                    'content_type':content_type,
                    'secret':secret,
                    'insecure_ssl':insecure_ssl,

                },
                'events':['push'],
                'active':True
            }
        print(f"测试参数: url={url}, content_type={content_type}, secret={secret},insecure_ssl={insecure_ssl}")
        with pytest.raises(Exception) as e:
                github_client.post(f'/repos/luciawang057-sudo/github-api-tests/hooks',json=webhook_data)
        assert_create_failure(e.value,expected_code=expected_code)
import pytest
import random



class TestUpdateWebhook:
    def test_update_webhook_smoke(self,github_client,factory_fixture_with_create_webhook):
        hookid=factory_fixture_with_create_webhook()
        update_data={
            'config': {
                'url': "https://123@qq.com/webhook",
                'content_type': "json",
                'secret': f'secret_{random.randint(100, 999)}',
                'insecure_ssl': '0'},
            'events': ['push'],
            'active': True
        }
        update_responsne=github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}',json=update_data)
        correct_data=update_responsne.json()
        correct_code=update_responsne.status_code
        print(f'正确的响应体：{correct_data}')
        print(f'正确的响应码：{correct_code}')

        assert 'id' in correct_data
        assert correct_data['id'] == hookid

        config_fields=['url','secret']
        for field in config_fields:
            assert field in correct_data['config']
            assert correct_data['config'][field] == update_data['config'][field]
        assert correct_data['config']['insecure_ssl'] == '0'
        # config_assertions = {
        #     'url': update_data['config']['url'],
        #     'secret': update_data['config']['secret'],
        #     'insecure_ssl': '0'
        # }
        #
        # for field, expected in config_assertions.items():
        #     assert correct_data['config'][field] == expected, f"config.{field} 不匹配"

        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')

    def test_update_webhook_with_add_and_remove(self, github_client, factory_fixture_with_create_webhook):
        hookid = factory_fixture_with_create_webhook()
        update_data={
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': ['pull_request','issues'],
            'remove_events': ['push']
        }
        update_responsne = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}',
                                               json=update_data)
        correct_data=update_responsne.json()
        assert 'id' in correct_data
        assert correct_data['id'] == hookid
        assert correct_data['events'] == ['pull_request','issues']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
#
class TestUpdateWebhookEventsBehavior:
    # 只有同时满足以下条件，remove 才会生效：
    # 1. 事件在 remove_events 中
    # 2. 事件不在 add_events 中
    # 3. 事件当前存在于 webhook 中
    # 如果事件在 add_events 中，无论是否在 remove_events 中，都会被保留
    def test_update_webhook_with_add_equal_remove_only_push(self, github_client, factory_fixture_with_create_webhook):

        hookid1 = factory_fixture_with_create_webhook()
        update_data1={
            'config': {
                'url': "https://example.com/webhook"},
            'add_events':  ['push'],
            'remove_events': ['push']
        }
        update_response1 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid1}',
                                                  json=update_data1)
        correct_data1 = update_response1.json()
        print(f'更新后events: {correct_data1["events"]}')
        assert correct_data1['events'] ==  ['push']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid1}')

    def test_update_webhook_with_only_remove(self, github_client, factory_fixture_with_create_webhook):
        hookid2 = factory_fixture_with_create_webhook()
        update_data2 = {
            'config': {
                'url': "https://example.com/webhook"},
            'remove_events': ['push']
        }
        update_response2 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid2}',
                                               json=update_data2)
        correct_data2 = update_response2.json()
        print(f'更新后events: {correct_data2["events"]}')
        assert correct_data2['events'] == []
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid2}')


    def test_update_webhook_with_add_equal_remove(self, github_client, factory_fixture_with_create_webhook):
        hookid3 = factory_fixture_with_create_webhook()
        update_data3 = {
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': ['push','pull_request'],
            'remove_events': ['push','pull_request']
        }
        update_response3 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid3}',
                                               json=update_data3)

        correct_data3 = update_response3.json()
        print(f'更新后events: {correct_data3["events"]}')
        assert correct_data3['events'] == ['push','pull_request']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid3}')

    def test_update_webhook_with_remove_noexist_type(self, github_client, factory_fixture_with_create_webhook):
        hookid4 = factory_fixture_with_create_webhook()
        update_data4 = {
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': ['push', 'pull_request'],
            'remove_events': ['push', 'invalid_type']
        }
        update_response4 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid4}',
                                               json=update_data4)

        correct_data4 = update_response4.json()
        print(f'更新后events: {correct_data4["events"]}')
        assert correct_data4['events'] == ['push', 'pull_request']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid4}')

    def test_update_webhook_with_add_noexist_type(self, github_client, factory_fixture_with_create_webhook):
        hookid5 = factory_fixture_with_create_webhook()
        update_data5 = {
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': ['invalid_type'],
            'remove_events': ['push']
        }
        with pytest.raises(Exception) as e:
             github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid5}',
                                               json=update_data5)
        assert hasattr(e.value, 'response')
        correct_data5 = e.value.response.json()
        print(f'错误的响应体：{correct_data5}')
        assert 'message' in correct_data5
        assert 'status' in correct_data5
        assert correct_data5['status'] == '422'

    def test_update_webhook_events_only_add(self, github_client,factory_fixture_with_create_webhook):
        hookid6= factory_fixture_with_create_webhook()
        update_data6 = {
        'config': {
            'url': "https://example.com/webhook"},
        'add_events': ['pull_request']
        }
        update_response6 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid6}',
                                           json=update_data6)

        correct_data6 = update_response6.json()
        print(f'更新后events: {correct_data6["events"]}')
        assert correct_data6['events'] == ['push', 'pull_request']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid6}')

    def test_update_webhook_events_with_None(self, github_client, factory_fixture_with_create_webhook):
        hookid7 = factory_fixture_with_create_webhook()
        update_data7 = {
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': [],
            'remove_events': []
        }
        update_response7 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid7}',
                                               json=update_data7)

        correct_data7 = update_response7.json()
        print(f'更新后events: {correct_data7["events"]}')
        assert correct_data7['events'] == ['push']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid7}')

    def test_update_webhook_events_with_partical_same(self, github_client, factory_fixture_with_create_webhook):
        hookid8 = factory_fixture_with_create_webhook()
        update_data8 = {
            'config': {
                'url': "https://example.com/webhook"},
            'add_events': ['pull_request', 'issues'],
            'remove_events': ['push','pull_request','issues']
        }
        update_response8 = github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid8}',
                                               json=update_data8)

        correct_data8 = update_response8.json()
        print(f'更新后events: {correct_data8["events"]}')
        assert correct_data8['events'] == ['push','pull_request','issues']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid8}')
class TestUpdateWebhookAllParams:
    def test_update_webhook_all_params(self, github_client,factory_fixture_with_create_webhook):
        hookid = factory_fixture_with_create_webhook()
        update_data = {
            'config': {
                'url': "https://example12134.com/webhook",
                'content_type': "form",
                'secret': f'secret_{random.randint(100, 999)}',
                'insecure_ssl': '0'
            },  # 这里加逗号
            'add_events': ['push', 'pull_request', 'issues','release'],
            'remove_events': ['pull_request','issues'],
            'active': False
        }  # 删除多余的括号
        update_response =github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}',json=update_data)
        correct_data = update_response.json()
        print(f'正确响应体：{correct_data}')
        assert isinstance(correct_data,dict)
        fields=['id','name','config','events','active']
        for field in fields:
            assert field in correct_data
        assert correct_data['id'] == hookid
        assert correct_data['name'] == 'web'
        assert correct_data['events'] == ['push', 'pull_request', 'issues','release']
        assert correct_data['active'] == False
        config_fields=['url','content_type','insecure_ssl']
        for field in config_fields:
            assert field in correct_data['config']
            assert correct_data['config'][field] == update_data['config'][field]

        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')

class TestUpdateWebhookWithWrongID:
    def test_update_webhook_with_invalid_id(self, github_client):
        hookid = 99999999
        update_data = {
            'config': {
                'url': "https://example12134.com/webhook",
                'content_type': "form"}}
        with pytest.raises(Exception) as e:
            github_client.patch(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}',json=update_data)
        assert hasattr(e.value, 'response')
        error_data = e.value.response.json()
        print(f'错误响应体：{error_data}')
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == '404'
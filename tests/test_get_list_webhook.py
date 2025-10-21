
import  pytest



class TestListWebhook:

    def test_list_webhook(self,github_client,factory_fixture_with_create_webhook):
        hookid=[]
        for i  in range (20):
            hook_id=factory_fixture_with_create_webhook()
            hookid.append(hook_id)
            print(f'创建第{i+1}个webhook，id为{hook_id}')




        test_cases=[
            {'page':1,'per_page':5,'expected_data':5},
            {'page':1,'per_page':10,'expected_data':10},
            {'page':2,'per_page':10,'expected_data':10},
            {'page':3,'per_page':10,'expected_data':0},
        ]
        for case in test_cases:
            response = github_client.get('/repos/luciawang057-sudo/github-api-tests/hooks', params=case)
            correct_data = response.json()
            correct_code=response.status_code
            print(f'正确响应体：{correct_data}')
            print(f'正确响应码：{correct_code}')
            print(f'页码{case["page"]},每页{case["per_page"]},返回数据{case["expected_data"]}')
            assert len(correct_data)==case['expected_data']

            for hook in correct_data:
                assert 'id' in hook
                assert 'name' in hook
                assert hook['name'] == 'web'
                assert 'events' in hook
                assert hook['events'] == ['push']
                assert 'url' in hook['config']



        for id in hookid:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{id}')

class TestGetAWebhook:
    def test_get_a_webhook(self, github_client, factory_fixture_with_create_webhook):
        hookid=factory_fixture_with_create_webhook()
        response=github_client.get(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
        correct_data=response.json()
        correct_code=response.status_code
        print(f'正确响应体：{correct_data}')
        print(f'正确响应码：{correct_code}')
        assert response.status_code==200
        assert 'id' in correct_data
        assert correct_data['id'] == hookid
        assert 'name' in correct_data
        assert correct_data['name'] == 'web'
        assert 'events' in correct_data
        assert correct_data['events'] == ['push']
        assert 'url' in correct_data['config']
        github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')

    def test_get_a_webhook_with_wrongid(self, github_client, factory_fixture_with_create_webhook):
        hookid=9999999999999
        with pytest.raises(Exception) as e:
             github_client.get(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
        assert hasattr(e.value, 'response')
        error_data = e.value.response.json()
        error_code=e.value.response.status_code
        print(f'错误响应体{error_data}')
        print(f'错误响应码{error_code}')
        assert 'message' in error_data
        assert error_data['status'] == '404'

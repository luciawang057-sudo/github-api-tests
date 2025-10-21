import random
import pytest
class TestCreateWebhookSmoke:
    def test_create_webhook_smoke(self,github_client):
        data={
            'name':f'test_webhook_{random.randint(100,999)}',
            'config':{
                'url':"https://example.com/webhook",
                'content-type':"application/json",
                'secret':"test-secret-123",
                'insecure_ssl':1
            },
            'events':['push'],
            'active':True
        }
        response = github_client.post('/repos/luciawang057-sudo/github-api-tests/hooks', json=data)
        correct_data =response.json()
        print(f'正确响应体：{correct_data}')
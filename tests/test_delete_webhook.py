import pytest


# class TestDeleteWebhook:
#     def test_delete_webhook(self,github_client,factory_fixture_with_create_webhook):
#         hookid=factory_fixture_with_create_webhook()
#         delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
#         assert delete_response.status_code == 204
#         with pytest.raises(Exception) as e:
#             github_client.get(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
#         assert hasattr(e.value, 'response')
#         assert e.value.response.status_code == 404

class TestDeleteWebhookCases:
    def test_delete_webhook_with_wrong_id(self,github_client):
        hookid=99999999999999
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid}')
        assert hasattr(e.value, 'response')
        error_data = e.value.response.json()
        error_code=e.value.response.status_code
        print(f'错误响应码：{error_code}')
        print(f'错误响应体：{error_data}')
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == '404'
    def test_delete_webhook_with_repeated(self,github_client,factory_fixture_with_create_webhook):
        hookid1=factory_fixture_with_create_webhook()
        first_delete = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid1}')
        assert first_delete.status_code == 204
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/hooks/{hookid1}')
        assert hasattr(e.value, 'response')
        assert e.value.response.status_code == 404


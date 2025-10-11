import pytest
def assert_fork_failure(exc_info,github_client):
    github_client.logger.error(f'创建fork失败: {exc_info.value}')

    error_data = exc_info.value.response.json()
    print(f'错误响应体：{error_data}')
    assert hasattr(exc_info.value, 'response')
    status_code = exc_info.value.response.status_code
    if status_code == 404:
        assert 'Not Found' in error_data['message']
    elif status_code == 422:
        assert 'Validation Failed' in error_data['message']
    elif status_code == 403:
        assert 'Name cannot be more than 100 characters' in error_data['message']

    assert 'status' in error_data and error_data['status'] in str(exc_info.value.response.status_code)


class TestCreateFork:
    @pytest.mark.smoke
    def test_create_fork_smoke(self,github_client):
        response = github_client.post('/repos/facebook/prophet/forks')
        assert response.status_code == 202
        print(f"响应内容：{response.json()}")
        assert isinstance(response.json(), dict)
        assert len(response.json())>0
        assert response.json()['fork']==True
        assert response.json()['full_name'] == 'luciawang057-sudo/prophet'
        assert response.json()['parent']['full_name'] =='facebook/prophet'
        assert response.json()['parent']['owner']['login'] == 'facebook'
        assert response.json()['source']['full_name'] == 'facebook/prophet'
        assert response.json()['source']['owner']['login'] == 'facebook'
        fields=['id','node_id','name','full_name','html_url','url','owner']
        for field in fields:
            assert field in response.json()
            assert 'login' in response.json()['owner']
            assert 'id' in response.json()['owner']
            assert 'node_id' in response.json()['owner']
        assert response.json()['owner']['login']=='luciawang057-sudo'
#
class TestCreateForkParams:
    def test_create_fork_with_wrong_owner(self,github_client):
        wrong_owner = 'a'*40
        with pytest.raises(Exception) as exc_info:
            github_client.post(f'/repos/{wrong_owner}/prophet/forks')
        assert_fork_failure(exc_info, github_client)

    def test_create_fork_with_wrong_repo(self,github_client):
        wrong_repo = 'a'*40
        with pytest.raises(Exception) as exc_info:
            github_client.post(f'/repos/facebook/{wrong_repo}/forks')
        assert_fork_failure(exc_info,github_client)


    def test_create_fork_own_repo(self,github_client):
        try:
            response=github_client.post('/repos/luciawang057-sudo/github-api-tests/forks')
            print(f'response={response.json()}')
            assert response.status_code == 202
            assert len(response.json())>0
            assert response.json()['fork']==False
        except Exception as e:
            assert_fork_failure(e, github_client)
            github_client.logger.error(f'未知错误：{e}')
    def test_fork_with_wrong_organization(self,github_client):
        organization='a'*100
        with pytest.raises(Exception) as e:
            github_client.post('/repos/facebook/pyre-check/forks',json={'organization':organization})
        github_client.logger.error(f'未知错误：{e.value}')
        assert_fork_failure(e, github_client)
    def test_repeat_fork(self,github_client):
        first_fork= github_client.post('/repos/facebook/react/forks')
        assert first_fork.status_code == 202
        assert len(first_fork.json())>0
        assert isinstance(first_fork.json(), dict)
        assert first_fork.json()['fork'] == True
        first_data=first_fork.json()
        print(f'第一次fork ID: {first_data["id"]}')

        second_fork= github_client.post('/repos/facebook/react/forks')
        assert second_fork.status_code == 202
        assert len(second_fork.json())>0
        assert isinstance(second_fork.json(), dict)
        second_data=second_fork.json()
        print(f'第二次fork ID: {second_data["id"]}')

        assert first_data["id"]==second_data["id"]
        assert first_data["full_name"]==second_data["full_name"]
        assert first_data["node_id"]==second_data["node_id"]
        #github_client.delete('/repos/luciawang057-sudo/react')



















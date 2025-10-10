
import pytest

from tests.conftest import github_client


class TestDeleteFile:
    @pytest.mark.smoke
    def test_delete_file(self,github_client,get_filename,get_author,get_committer):
        jsondata = {
            'message':'test message',
            'content':"bXkgbmV3IGZpbGUgY29udGVudHM=",
            'author':get_author,
            'committer':get_committer,
        }
        response1 = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=jsondata)
        assert response1.status_code in [200, 201]
        assert isinstance(response1.json(), dict)
        assert 'content' in response1.json()
        assert len(response1.json()['content']) > 0
        assert response1.json()['commit']['message'] == jsondata['message']
        file_sha=response1.json()['content']['sha']

        delete_data={
            'message': 'test message',
            'sha': file_sha,
            'author': get_author,
            'committer': get_committer,

        }
        response2=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert response2.status_code ==200
        assert response2.json()['content'] is None
        assert 'commit'in response2.json()
        assert 'committer' in response2.json()['commit']
        print(f'响应体：{response2.json()}')




class TestDeleteFileConflict:
    def test_delete_with_wrong_sha(self,github_client,get_filename,get_author,get_committer):
        jsondata = {
            'message': 'test_wrong_sha',
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'author':get_author,
            'committer':get_committer
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=jsondata)
        wrong_sha='a'*40
        assert response.status_code in [200, 201]
        assert isinstance(response.json(), dict)
        assert 'content' in response.json()
        assert len(response.json()['content']) > 0
        delete_data={
            'message': 'test_wrong_sha',
            'author': get_author,
            'committer': get_committer,
            'sha': wrong_sha,
        }
        try:
            delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
            assert 'Error' in delete_response.json()
        except Exception as e:
            if hasattr(e,'response'):
                assert e.response.status_code == 409
                print(f'删除返回的响应体：{e.response.json()}')


    def test_delete_without_sha(self,github_client,get_filename,get_author,get_committer):
        jsondata = {
            'message': 'test_wrong_sha',
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'author': get_author,
            'committer': get_committer
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=jsondata)

        assert response.status_code in [200, 201]
        assert isinstance(response.json(), dict)
        assert 'content' in response.json()
        assert len(response.json()['content']) > 0
        delete_data = {
            'message': 'test_wrong_sha',
            'author': get_author,
            'committer': get_committer,
        }
        try:
            delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
            assert '422' in delete_response.json() or 'Error' in delete_response.json()
        except Exception as e:
            if hasattr(e, 'response'):
                assert e.response.status_code == 422
                print(f'删除返回的响应体：{e.response.json()}')

    def test_delete_with_invalid_repo(self,github_client,get_filename,get_author,get_committer,get_sha):
        file_sha=get_sha['sha']
        filename =get_sha['filename']
        delete_data = {
            'message': 'test_wrong_repo',
            'author': get_author,
            'committer': get_committer,
            'sha': file_sha,
        }
        try:
            delete_reponse=github_client.delete(f'/repos/luciawang057-sudo/tests/contents/{filename}',json=delete_data)
            assert '404' in delete_reponse.json() or 'Error' in delete_reponse.json()
        except Exception as e:
            if hasattr(e,'response'):
                assert e.response.status_code == 404
                print(f'删除返回的响应体：{e.response.json()}')

    def test_delete_with_invalid_owner(self,github_client,get_filename,get_author,get_committer,get_sha):
        file_sha=get_sha['sha']
        filename =get_sha['filename']
        delete_data = {
            'message': 'test_wrong_owner',
            'author': get_author,
            'committer': get_committer,
            'sha': file_sha,
        }
        try:
            delete_reponse=github_client.delete(f'/repos/luciawyx/github-api-tests/contents/{filename}',json=delete_data)
            assert '404' in delete_reponse.json() or 'Error' in delete_reponse.json()
        except Exception as e:
            if hasattr(e,'response'):
                assert e.response.status_code == 404
                print(f'删除返回的响应体：{e.response.json()}')

    def test_delete_with_noexist_branch(self,github_client,get_filename,get_author,get_committer,get_sha):
        file_sha=get_sha['sha']
        filename =get_sha['filename']
        delete_data = {
            'message': 'test_wrong_branch',
            'author': get_author,
            'committer': get_committer,
            'sha': file_sha,
            'branch': 'first_branch',
        }
        try:
            delete_reponse=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}',json=delete_data)
            assert '404' in delete_reponse.json() or 'Error' in delete_reponse.json()
        except Exception as e:
            if hasattr(e,'response'):
                assert e.response.status_code == 404
                print(f'删除返回的响应体：{e.response.json()}')

    def test_delete_repeated(self,github_client,get_filename,get_author,get_committer):
        create_data = {
            'message':'delete_repeate_file',
            'content':'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'author':get_author,
            'committer':get_committer,
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=create_data)
        assert response.status_code in (200,201)
        assert isinstance(response.json(), dict)
        assert 'content' in response.json()
        assert len(response.json()['content']) > 0
        file_sha = response.json()['content']['sha']
        assert response.json()['commit']['message'] == create_data['message']
        delete_data={
            'message':'delete_repeate_file',
            'author':get_author,
            'committer':get_committer,
            'sha':file_sha,
        }
        first_delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert first_delete_response.status_code == 200
        try:
            second_delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
            print(f'预期错误响应体：{second_delete_response.json()}')
        except Exception as e:
            if hasattr(e,'response'):
                print(f'错误e响应体：{e.response.json()}')
                assert e.response.status_code == 404
                assert 'Error ' in e.response.json() or 'message' in e.response.json()




class TestDeleteParameterValidation:
    @pytest.mark.parametrize('owner,repo,path,expected_code', [
        # owner边界
        (None, 'github-api-tests', 'fixed_test_file.txt', 404),
        ('', 'github-api-tests', 'fixed_test_file.txt', 404),
        (' ', 'github-api-tests', 'fixed_test_file.txt', 404),
        ('c' * 1000, 'github-api-tests', 'fixed_test_file.txt', 404),
        ('%$$^zhong%$$^zhong', 'github-api-tests', 'fixed_test_file.txt', 404),
        # repo边界
        ('luciawang057-sudo', None, 'fixed_test_file.txt', 404),
        ('luciawang057-sudo', '', 'fixed_test_file.txt', 404),
        ('luciawang057-sudo', ' ', 'fixed_test_file.txt', 404),
        ('luciawang057-sudo', 'c' * 1000, 'fixed_test_file.txt', 404),
        ('luciawang057-sudo', '%$$^zhong%$$^zhong', 'fixed_test_file.txt', 404),
        # path边界
        ('luciawang057-sudo', 'github-api-tests', None, 422),
        ('luciawang057-sudo', 'github-api-tests', '', 404),
        ('luciawang057-sudo', 'github-api-tests', ' ', 422),
        ('luciawang057-sudo', 'github-api-tests', 'c' * 1000, 422),
        ('luciawang057-sudo', 'github-api-tests', '%$$^zhong%$$^zhong', 422)

    ])
    def test_validate_with_owner_repo_path(self,github_client,owner,repo,path,get_author,get_committer,expected_code,get_sha):
        file_sha=get_sha['sha']
        json_data = {
            'message':'test_validate_with_owner_repo_path',
            'author':get_author,
            'sha': file_sha,
            'committer':get_committer,

        }
        try:
            delete_response=github_client.delete(f'/repos/{owner}/{repo}/contents/{path}',json=json_data)
            assert delete_response.status_code==expected_code
            assert 'Error' in delete_response.json()
        except Exception as e:
            if hasattr(e,'response'):
                assert e.response.status_code==expected_code

    @pytest.mark.parametrize('message,expected_code', [
        # message边界
        (None, 422),
        ('',  422),
        (' ',422),
        (123,422),
        ('a' * 1000, 422),
        ('#$%^&&', 422),

    ])
    def test_validate_with_message(self, github_client,message,get_author, get_committer,expected_code, get_sha):
        file_sha = get_sha['sha']
        filename= get_sha['filename']
        json_data = {
            'message': message,
            'author': get_author,
            'sha': file_sha,
            'committer': get_committer,

        }
        try:
            delete_response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}', json=json_data)
            assert delete_response.status_code == expected_code
            assert 'Error' in delete_response.json()
            print(f'Message测试 - message:"{message}", 状态码:{delete_response.status_code}')
        except Exception as e:
            if hasattr(e, 'response'):
                print(f'Message测试 - message:"{message}", 状态码:{e.response.status_code}')
                assert e.response.status_code == expected_code








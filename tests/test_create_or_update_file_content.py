
import pytest

import requests

from requests import HTTPError
def assert_create_content_success(response,json_data):
    assert response.status_code in [200, 201]
    assert isinstance(response.json(), dict)
    assert 'content' in response.json()
    assert len(response.json()['content']) > 0
    print(f'响应内容中的content{response.json().get("content")}')
def assert_create_content_failure(exception,json_data=None):
    assert hasattr(exception, 'response'),f"异常对象没有response属性: {type(exception)}"
    status_code = exception.response.status_code
    print(f'错误响应码：{status_code}')
    try:
        error_response = exception.response.json()
        print(f'错误响应体(JSON)：{error_response}')
    except requests.exceptions.JSONDecodeError:
        error_response_text = exception.response.text
        print(f'错误响应体(文本)：{error_response_text[:200]}...')  # 只打印前200字符
        error_response = {'raw_text': error_response_text}  # 创建一个包含原始文本的字典

    if status_code == 404:
        assert 'message' in error_response
        assert error_response['status'] == '404'
    elif status_code == 409:
        assert 'message' in error_response
        assert error_response['status'] == '409'
    elif status_code == 422:
        assert error_response['status'] == '422'
    elif status_code == 500:
        print('⚠️  服务器内部错误(500)，跳过响应体结构验证')

    else:
        if 'status' in error_response:
            assert 'status' in error_response,f"错误响应体中没有status字段: {error_response},{status_code}"
        else:
            pass



class TestCreateOrUpdateFileContent:
    @pytest.mark.smoke
    def test_create_file_content_get_sha(self, github_client,get_filename):
        createdata={
        'message':'test message',
        'content': "bXkgbmV3IGZpbGUgY29udGVudHM="
    }
        response1=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=createdata)
        assert_create_content_success(response1,createdata)
        file_sha=response1.json()["content"]['sha']
        print(f'获取文件的sha{file_sha}')
        updatedata = {
        'message': 'test message',
        'content': "bXkgbmV3IGZpbGUgY29udGVudHM=",
        'sha': file_sha
    }
        response2=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=updatedata)
        assert_create_content_success(response2, updatedata)


class TestCreateSuccess:
    '''主要测 message, content, branch, committer, author 的各种正常组合,
    固定：正确的 owner, repo, path'''

@pytest.mark.parametrize('message,content,branch,expect_code',[
    ('test message',"bXkgbmV3IGZpbGUgY29udGVudHM=",'main',200),
    ('123','JXU2MjExJXU1NTlDJXU2QjIycHl0aG9u','main',200),
    ('wyx','JXU1MkFBJXU1MjlCJXU1QjY2JXU0RTYwJXU4MUVBJXU1MkE4JXU1MzE2','main',200)])
def test_create_success(github_client,get_filename,message,content,branch,get_committer,get_author,expect_code):

        json_data={
        'message': message,
        'content': content,
        'branch': branch,
        'committer': get_committer,
        'author': get_author
        }
        response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=json_data)
        print(f'响应内容{response.json()}')
        if response.status_code ==200 or response.status_code ==201:
            assert_create_content_success(response, json_data)
            fields=['name','path','sha','size','url','html_url','download_url']
            for field in fields:
                assert field in response.json()['content']

            assert response.json()['commit']['message']==json_data['message']
            assert response.json()['commit']['committer']['name'] == json_data['committer']['name']
            assert response.json()['commit']['committer']['email'] == json_data['committer']['email']
            assert response.json()['commit']['author']['name']==json_data['author']['name']
            assert response.json()['commit']['author']['email']==json_data['author']['email']



class TestCreateFileConflict:
    '''主要测 owner, repo, path, sha 的业务逻辑错误，测试业务逻辑约束变化：
    错误的owner、错误的repo、重复文件路径'''
    def test_update_file_with_wrong_sha_409(self,github_client,get_filename):
        jsondata = {
                 'message':'test messagetest message',
                 'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'
            }
        response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=jsondata)
        assert_create_content_success(response, jsondata)
        error_data = {
            'message':'test messagetest message',
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'sha':"a" * 40

        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=error_data)
        assert_create_content_failure(e.value,error_data)





    def test_update_without_sha_422(self,github_client,get_filename):
        json_data={
            'message':'test message'*10,
            'content':'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'
        }
        response =github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=json_data)
        assert_create_content_success(response, json_data)

        update_data_without_sha={
            'message':'test message'*10,
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'

        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=update_data_without_sha)
        assert_create_content_failure(e.value,update_data_without_sha)

        file_sha = response.json()['content']['sha']
        delete_data = {
            'message': 'cleanup test file',
            'sha': file_sha
        }
        github_client.delete(
            f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',
            json=delete_data
        )

    def test_wrong_repo_404(self,github_client,get_filename):
        json_data={
            'message': 'test message' * 10,
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'
        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawang057-sudo/wrong_repo/contents/{get_filename}', json=json_data)
        assert_create_content_failure(e.value, json_data)

    def test_nonexistent_branch_404(self,github_client,get_filename):
        json_data={
        'message': 'test message' * 10,
        'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
        'branch':'wrong_branch'
        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}', json=json_data)
        assert_create_content_failure(e.value, json_data)
    def test_wrong_owner_404(self, github_client, get_filename):
        json_data={
        'message': 'test message' * 10,
        'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'
        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/luciawangwyx/github-api-tests/contents/{get_filename}', json=json_data)
        assert_create_content_failure(e.value, json_data)

class TestUpdateFileSuccess:
    '''主要测 SHA 的正确使用,固定：正确的 owner, repo, path,变化：正确的SHA vs 错误的SHA'''
    def test_update_success(self, github_client,get_filename):
        json_data = {
            'message': 'test message' * 10,
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5'
            }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=json_data)
        assert_create_content_success(response,json_data)
        true_sha= response.json()['content']['sha']
        assert response.json()['commit']['message'] == json_data['message']

        updated_json_data = {
            'message': 'test message' * 20,
            'content': 'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'sha': true_sha
        }
        response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=updated_json_data)
        assert_create_content_success(response,json_data)
        assert response.json()['commit']['message']==updated_json_data['message']

class TestParameterValidation:
    '''主要测所有参数的格式边界问题,变化：None, '', '   ', 超长字符等边界值目标：验证 422 参数校验失败'''
    @pytest.mark.parametrize('owner,repo,path,expected_code', [
        #owner边界
        (None,'github-api-tests','fixed_test_file.txt',404),
        ('','github-api-tests','fixed_test_file.txt',404),
        (' ','github-api-tests','fixed_test_file.txt',404),
        ('c'*1000,'github-api-tests','fixed_test_file.txt',404),
        ('%$$^zhong%$$^zhong','github-api-tests','fixed_test_file.txt',404),
        #repo边界
        ('luciawang057-sudo',None, 'fixed_test_file.txt',404),
        ('luciawang057-sudo','', 'fixed_test_file.txt',404),
        ('luciawang057-sudo',' ','fixed_test_file.txt',404),
        ('luciawang057-sudo','c'*1000,'fixed_test_file.txt',404),
        ('luciawang057-sudo','%$$^zhong%$$^zhong','fixed_test_file.txt', 404),
        #path边界
        ('luciawang057-sudo','github-api-tests',None,422),
        ('luciawang057-sudo', 'github-api-tests','', 404),
        ('luciawang057-sudo', 'github-api-tests', ' ', 422),
        ('luciawang057-sudo', 'github-api-tests','c'*1000,422),
        ('luciawang057-sudo', 'github-api-tests', '%$$^zhong%$$^zhong',422)

    ])
    def test_validate_with_owner_repo_path(self, github_client, owner, repo, path,get_author,get_committer,expected_code):
        json_data = {
            'message': 'test message' * 10,
            'content':'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
            'committer':get_committer,
            'author':get_author,

        }
        with pytest.raises(Exception) as e:
            github_client.put(f'/repos/{owner}/{repo}/contents/{path}',json=json_data)
        assert_create_content_failure(e.value,json_data)

    @pytest.mark.parametrize('message,content,expected_code', [
        #message边界
        (None,'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',422),
        ('','JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',201),
        (' ','JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',201),
        (123,'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',422),
        ('a'*1000,'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',201),
        ('#$%^&&','JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',201),
        #content边界
        ('test message',None,422),
        ('test message','',201),
        ('test message',' ',422),
        ('test message',123,422),
        ('test message','a'*1000,201),
        ('test message','#$%^&&&===',422),
    ])
    def test_invalid_message_content(self,github_client,message,content,expected_code,get_filename,get_author,get_committer):
        json_data={
            'message':message,
            'content':content,
            'author':get_author,
            'committer':get_committer,
        }


        if expected_code in [200,201]:
            response = github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',
                                         json=json_data)
            assert response.status_code == expected_code, f"期望状态码{expected_code}，实际得到{response.status_code}"

            assert_create_content_success(response,json_data)

            file_sha = response.json()['content']['sha']
            delete_data = {'message': 'cleanup','sha': file_sha}
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}', json=delete_data)
        else:
            with pytest.raises(Exception) as e:
                github_client.put(
                    f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',
                    json=json_data
                )
                # 验证失败响应
            assert_create_content_failure(e.value, json_data)




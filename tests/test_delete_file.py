
import pytest




def assert_delete_success(response ,json, github_client):#用来验证删除前的成功创建
    assert response.status_code in [200, 201]
    correct_data = response.json()
    print(f"正确数据：{correct_data}")
    assert isinstance(correct_data, dict)
    if 'content' in correct_data and correct_data['content'] is not None:
        assert len(correct_data['content']) >= 0  # 允许空内容
    # 如果没有 content 字段也是正常的
    assert 'commit' in correct_data
    if json['message'] in ('',' '):
        assert correct_data['commit']['message'] ==''
    elif json['message'].startswith(' ') or json['message'].endswith(' '):
        assert correct_data['commit']['message'] ==json['message'].strip()
    else:
        assert correct_data['commit']['message']==json['message']




def assert_delete_failure(exception, json, github_client):
    assert hasattr(exception, 'response')
    error_data = exception.response.json()
    error_code = exception.response.status_code
    print(f"错误数据：{error_data}")
    print(f"错误响应码：{error_code}")
    if error_code == 409:
        assert 'message' in error_data
        assert  'status' in error_data
        assert  error_data['status'] == '409'
    elif error_code == 422:
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == '422'
    elif error_code == 404:
        assert 'message' in error_data
        assert 'status' in error_data
        assert error_data['status'] == '404'
    else:
        if 'status' in error_data:
            assert 'status' in error_data, f"错误响应体中没有status字段: {error_data},{error_code}"
        else:
            github_client.logger.error(f'记录错误{error_data},{error_code}')


class TestDeleteFile:
    @pytest.mark.smoke
    def test_delete_file(self,github_client,factory_fixture_with_delete_file,get_committer,get_filename,get_author):
        file_sha=factory_fixture_with_delete_file()
        delete_data={
            'message': 'test message',
            'sha': file_sha,
            'author': get_author,
            'committer': get_committer,

        }
        response2=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert_delete_success(response2, delete_data, github_client)



class TestDeleteFileConflict:
    def test_delete_with_wrong_sha(self,github_client,get_filename,get_author,get_committer,factory_fixture_with_delete_file):
        file_sha=factory_fixture_with_delete_file()
        wrong_sha='a'*40

        delete_data={
            'message': 'test_wrong_sha',
            'author': get_author,
            'committer': get_committer,
            'sha': wrong_sha,
        }
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert_delete_failure(e.value,delete_data, github_client)

    def test_delete_without_sha(self,github_client,get_filename,get_author,get_committer,factory_fixture_with_delete_file):
        file_sha=factory_fixture_with_delete_file()
        delete_data = {
            'message': 'test_wrong_sha',
            'author': get_author,
            'committer': get_committer,
        }
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert_delete_failure(e.value,delete_data, github_client)

    # def test_delete_with_invalid_repo(self,github_client,get_filename,get_author,get_committer,get_sha):
    #     file_sha=get_sha['sha']
    #     filename =get_sha['filename']
    #     delete_data = {
    #         'message': 'test_wrong_repo',
    #         'author': get_author,
    #         'committer': get_committer,
    #         'sha': file_sha,
    #     }
    #     with pytest.raises(Exception) as e:
    #         github_client.delete(f'/repos/luciawang057-sudo/repotest/contents/{filename}', json=delete_data)
    #     assert_delete_failure(e.value, delete_data, github_client)
    #
    # def test_delete_with_invalid_owner(self,github_client,get_filename,get_author,get_committer,get_sha):
    #     file_sha=get_sha['sha']
    #     filename =get_sha['filename']
    #     delete_data = {
    #         'message': 'test_wrong_owner',
    #         'author': get_author,
    #         'committer': get_committer,
    #         'sha': file_sha,
    #     }
    #     with pytest.raises(Exception) as e:
    #         github_client.delete(f'/repos/luciawangwyx/github-api-tests/contents/{filename}',json=delete_data)
    #     assert_delete_failure(e.value,delete_data, github_client)
    #
    # def test_delete_with_noexist_branch(self,github_client,get_filename,get_author,get_committer,get_sha):
    #     file_sha=get_sha['sha']
    #     filename =get_sha['filename']
    #     delete_data = {
    #         'message': 'test_wrong_branch',
    #         'author': get_author,
    #         'committer': get_committer,
    #         'sha': file_sha,
    #         'branch': 'first_branch',
    #     }
    #     with pytest.raises(Exception) as e:
    #         github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}', json=delete_data)
    #     assert_delete_failure(e.value, delete_data, github_client)


    def test_delete_repeated(self,github_client,get_filename,get_author,get_committer,factory_fixture_with_delete_file):
        file_sha=factory_fixture_with_delete_file()

        delete_data={
            'message':'delete_repeate_file',
            'author':get_author,
            'committer':get_committer,
            'sha':file_sha,
        }
        first_delete_response=github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}',json=delete_data)
        assert first_delete_response.status_code == 200
        with pytest.raises(Exception) as e:
            github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{get_filename}', json=delete_data)
        assert_delete_failure(e.value, delete_data, github_client)




# class TestDeleteParameterValidation:
#     @pytest.mark.parametrize('owner,repo,path,expected_code', [
#         # owner边界
#         (None, 'github-api-tests', 'fixed_test_file.txt', 404),
#         ('', 'github-api-tests', 'fixed_test_file.txt', 404),
#         (' ', 'github-api-tests', 'fixed_test_file.txt', 404),
#         ('c' * 1000, 'github-api-tests', 'fixed_test_file.txt', 404),
#         ('%$$^zhong%$$^zhong', 'github-api-tests', 'fixed_test_file.txt', 404),
#         # repo边界
#         ('luciawang057-sudo', None, 'fixed_test_file.txt', 404),
#         ('luciawang057-sudo', '', 'fixed_test_file.txt', 404),
#         ('luciawang057-sudo', ' ', 'fixed_test_file.txt', 404),
#         ('luciawang057-sudo', 'c' * 1000, 'fixed_test_file.txt', 404),
#         ('luciawang057-sudo', '%$$^zhong%$$^zhong', 'fixed_test_file.txt', 404),
#         # path边界
#         ('luciawang057-sudo', 'github-api-tests', None, 404),
#         ('luciawang057-sudo', 'github-api-tests', '',404),
#         ('luciawang057-sudo', 'github-api-tests', ' ',422),
#         ('luciawang057-sudo', 'github-api-tests', 'c' * 1000,404),
#         ('luciawang057-sudo', 'github-api-tests', '%$$^zhong%$$^zhong',422)
#
#     ])
#     def test_validate_with_owner_repo_path(self,github_client,owner,repo,path,get_author,get_committer,expected_code,get_sha):
#         file_sha=get_sha['sha']
#         json_data = {
#             'message':'test_validate_with_owner_repo_path',
#             'author':get_author,
#             'sha': file_sha,
#             'committer':get_committer,
#
#         }
#         if expected_code==200:
#             response=github_client.delete(f'/repos/{owner}/{repo}/contents/{path}',json=json_data)
#             assert_delete_success(response, json_data, github_client)
#         else:
#             with pytest.raises(Exception) as e:
#                 github_client.delete(f'/repos/{owner}/{repo}/contents/{path}', json=json_data)
#             assert_delete_failure(e.value, json_data, github_client)
#
#     @pytest.mark.parametrize('message,expected_code', [
#         # message边界
#         (None,422),
#         ('',200),
#         (' ',200),
#         ('aoc ',200),
#         (123,422),
#         ('a' * 1000,200),
#         ('#$%^&&',200),
#
#     ])
#     def test_validate_with_message(self, github_client,message,get_author, get_committer,expected_code, get_sha):
#         file_sha = get_sha['sha']
#         filename= get_sha['filename']
#         json_data = {
#             'message': message,
#             'author': get_author,
#             'sha': file_sha,
#             'committer': get_committer,
#
#         }
#         if expected_code == 200:
#             response = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}', json=json_data)
#             assert_delete_success(response, json_data, github_client)
#         else:
#             with pytest.raises(Exception) as e:
#                 github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}', json=json_data)
#             assert_delete_failure(e.value, json_data, github_client)









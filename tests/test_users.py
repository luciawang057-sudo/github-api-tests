
import pytest
import json
from requests import HTTPError


class TestUsers:
    @pytest.mark.smoke
    def testgetAuthenticatedUser(self,github_client):

        response=github_client.get('/user')
        assert response.status_code == 200
        print("🔍 实际返回的数据:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))


        assert isinstance(response.json(), dict)


        assert 'id' in response.json()
        assert "user_view_type" in response.json()
        assert "node_id" in response.json()
        assert 'avatar_url' in response.json()
        assert 'gravatar_id' in response.json()
        assert 'url' in response.json()
        assert 'html_url' in response.json()

    def testgetAuthenticatedUser_unauthorized(self):
        from utils.github_client import GithubClient
        invalid_client=GithubClient(token='ghp_a0AEareoybalBlU6pouHW5jZdfDSSSSSSWEFSFADA')
        with pytest.raises(Exception)  as exc_info:
            invalid_client.get('/user')
        print("🔍 exc_info.value 内容:", exc_info.value)
        # print("🔍 exc_info 内容:", exc_info)
        # print("🔍str(exc_info) 内容:",str(exc_info))
        assert '401' in str(exc_info.value)

    def testgetAuthenticatedUser_no_token(self):
        from utils.github_client import GithubClient
        invalid_client=GithubClient(token=None)
        with pytest.raises(Exception) as exc_info:
            invalid_client.get('/user')
        print("🔍 exc_info.value 内容:", exc_info.value)
        # print("🔍 exc_info内容:", exc_info)
        # print("🔍str(exc_info) 内容:", str(exc_info))

        assert '401' in str(exc_info.value)

# pytest.raises() 的工作原理：
# with pytest.raises(HTTPError) as exc_info:
#     # 这里的代码必须抛出 HTTPError
#     invalid_client.get('/user')
# 关键点：
# 只有匹配指定异常类型的异常才会被捕获
# 如果抛出的异常类型不匹配，测试会失败
# 如果没有抛出任何异常，测试也会失败
# exc_info.type - 获取异常类型
# exc_info.value - 获取异常实例
# exc_info.traceback - 获取调用栈
    @pytest.mark.smoke
    @pytest.mark.parametrize('account_id,expected_status_code', [
        (1,200),(0,404),(-2,404),(9.987,404),(999999999999999,404)
    ] )
    def test_get_a_user_using_their_id(self,github_client,account_id,expected_status_code):

        try:
            response = github_client.get(f'/user/{account_id}')
            assert response.status_code == expected_status_code
            if expected_status_code==200:
                assert response.status_code == 200
                assert response.json().get('id') == account_id

        except HTTPError as e:#e 就是捕获到的异常对象,类似于错误响应
            assert expected_status_code == 404,f'希望是404，实际上是{response.status_code}'
            assert e.response.status_code == 404
            github_client.logger.info(f"预期中的404异常: {e}")

    @pytest.mark.smoke
    @pytest.mark.parametrize('since,per_page,expected_status_code', [
        (1,30,200),(0,30,200),(-1,30,200),(None,None,200),(1,100,200),(1,101,200),(9999999999,30,200)
    ])
    def test_list_users(self,github_client,since,per_page,expected_status_code):
        try:
            params={
                'since': since,
                'per_page': per_page,
            }
            responses = github_client.get(f'/users',params=params)
            assert responses.status_code == expected_status_code
            if expected_status_code==200:
                assert responses.status_code == 200
                assert isinstance(responses.json(),list)
                for user in responses.json():
                    assert isinstance(user,dict)
                    user_tuple=[('id',int),('login',str),('avatar_url',str),('url',str),('html_url',str)]
                    for field_name,expect_type in user_tuple:
                        assert isinstance(user[field_name],expect_type)
                        assert field_name in user
        except HTTPError as e:
            assert expected_status_code == 422
            assert e.response.status_code == 422
            github_client.logger.info(f'错误为{e}')

    @pytest.mark.smoke
    @pytest.mark.parametrize('user_name,expected_status_code', [
        ('octocat',200),(None,404),(123,200),('OCTOCAT',200),('',404),(' ',404),('a',200),('invalid_username_999',404)
    ])
    def test_get_a_user(self,github_client,user_name,expected_status_code):
        try:
            response = github_client.get(f'/users/{user_name}')
            assert response.status_code == expected_status_code
            if expected_status_code==200:
                assert isinstance(response.json(), dict)
                field_type=['id','login','avatar_url','url','html_url']
                for field in field_type:
                    assert field in response.json()
                if isinstance(user_name,str):
                    assert response.json()['login'].lower()==user_name.lower()


        except HTTPError as e:
            assert expected_status_code == 404
            assert e.response.status_code == 404
            github_client.logger.error(f'预期错误:{e}')




    @pytest.mark.parametrize('user_name,subject_type,subject_id,expected_status_code', [
        ('octocat', None, None, 200),
        ('octocat', 'repository', None, 200),  # 只提供类型，不提供ID
        ('octocat', 'organization', None, 200),
        ('octocat','123','123',404),
        ('invalid_user',None,None,404),
        ('octocat', 'repository', 'invaild_id', 404),
        ('octocat', 'invalid_type', '123', 404),
        ('octocat', 'invalid_type', 'invaild_id', 404),
        ('octocat', 'repository',None, 200),
        ('octocat', None, '123', 404),
        ('', None, None, 404),                    # 空用户名
        ('octocat', '', '123', 404),              # 空类型
        ('octocat', 'repository', '', 404),     # 空ID
        ('a' * 100, None, None, 404),  # 超长用户名
        ('octocat', 'a' * 50, '123', 404) # 超长类型

    ])
    def test_get_contextual_information_for_a_user(self,github_client,user_name,subject_type,subject_id,expected_status_code):

        try:
            params={
            'subject_type': subject_type,
            'subject_id': subject_id,
            }
            response=github_client.get(f'/users/{user_name}/hovercard',params=params)
            assert response.status_code == expected_status_code
            if expected_status_code == 200:

                data = response.json()
                assert 'contexts' in data

            elif expected_status_code == 422:
                assert len(response.json())==0


        except HTTPError as e:
            assert expected_status_code ==404
            assert e.response.status_code == 404
            github_client.logger.info(f'预期错误{e}')



    def test_contextual_info_with_real_ids(self, github_client):
            repo_response=github_client.get('/repos/rails/rails')
            repo_id=repo_response.json()['id']
            org_response=github_client.get('/orgs/github')
            org_id=org_response.json()['id']
            # # 定义测试用例
            #
            # test_cases = [
            #     ('repository', repo_id),
            #     ('organization', org_id)
            # ]
            #
            # for subject_type, subject_id in test_cases:
            #     response = github_client.get(
            #         '/users/octocat/hovercard',
            #         params={'subject_type': subject_type, 'subject_id': subject_id}
            #     )
            #     print(f'{subject_type}类型响应: {response.json()}')

            response1=github_client.get('/users/octocat/hovercard',params={'subject_type': 'repository','subject_id': repo_id})
            print(f'响应内容为{response1.json()}')
            assert response1.status_code == 200
            assert 'contexts' in response1.json()
            assert isinstance(response1.json()['contexts'], list)

            response2=github_client.get('/users/octocat/hovercard',params={'subject_type': 'organization','subject_id': org_id})
            print(f'响应内容为{response2.json()}')
            assert response2.status_code == 200
            assert 'contexts' in response2.json()
            assert isinstance(response2.json()['contexts'], list)
















import pytest

def assert_fork_success(response,param_data):
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert isinstance(response.json(), list)
    print(f'返回的响应体:{response.json()}')
    fields = ['id', 'name', 'full_name', 'html_url', 'fork', 'url']
    for fork_repo in response.json():  # 遍历返回的每个fork项目
        for field in fields:
            assert field in fork_repo  ## 验证这个fork项目包含必要字段
        assert fork_repo['fork'] == True
        assert 'login' in fork_repo['owner']
        assert 'id' in fork_repo['owner']
        assert 'node_id' in fork_repo['owner']
        assert 'html_url' in fork_repo['owner']
        assert 'url' in fork_repo['owner']
def assert_fork_failure(exception,expected_code,github_client):
    assert hasattr(exception, 'response')
    error_data = exception.response.json()
    print(f'返回响应体：{error_data}')
    assert exception.response.status_code == expected_code
    if expected_code == 404:
            assert 'status' in error_data
            assert 'message' in error_data
            assert error_data['status'] == f'{expected_code}'
            assert 'Not Found' in error_data['message']
    elif expected_code == 400:
        print(f'返回的错误e响应体:{error_data}')
        assert 'message' in error_data
        assert error_data['status'] == f'{expected_code}'

    else:
        github_client.logger.error(f'未知错误{exception}')

class TestFork:
    @pytest.mark.smoke
    def test_list_fork_smoke(self,github_client):
        param_data={
            'sort':'newest',
            'page':1,
            'per_page':30
        }
        response=github_client.get('/repos/facebook/react/forks',params=param_data)
        assert_fork_success(response,param_data)


class TestlistForkCases:
    @pytest.mark.parametrize('sort,expected_code',[
        ('oldest',200),('stargazers',200),('watchers',200),(123,400),(None,200),('',400),(' ',400),('WYX',400)
    ])
    def test_list_fork_sort_param(self,github_client,sort,expected_code):
        param_data={
            'sort':sort,
            'page':1,
            'per_page':30
        }
        try:
            response = github_client.get('/repos/facebook/react/forks',params=param_data)
            if expected_code==200:
                assert_fork_success(response,param_data)

        except Exception as e:
            assert_fork_failure(e,expected_code,github_client)


    @pytest.mark.parametrize('page,per_page',[
        #page边界
        (0,30), (-1,30),(None,30),('wux',30),('',30),(' ',30),(1.9,30),
        #per_page边界
        (1,30),(1,100),(1,101),(1,-1),(1,None),(1,'wux'),(1,''),(1,' '),(1,1.9),(1,0),
        (1,1),
        #双重
        (None,None)
    ])
    def test_list_fork_page_params(self,github_client,page,per_page):

        param_data={
            'sort':'newest'
        }
        if page is not None:
            param_data['page'] = page
        if per_page is not None:
            param_data['per_page'] = per_page

        response=github_client.get('/repos/facebook/react/forks',params=param_data)
        assert response.status_code == 200
        assert isinstance(response.json(),list)
        assert len(response.json())>=0

        data_count = len(response.json())

        if per_page is None:
            print(f'默认分页：30条，实际：{data_count}条')
        elif isinstance(per_page, int) and 1 <= per_page <= 100:
            print(f'设置分页：{per_page}条，实际：{data_count}条')
        elif isinstance(per_page, int) and per_page > 100:
            print(f'分页超限：{per_page}→100条，实际：{data_count}条')
        else:
            print(f'无效分页："{per_page}"→30条，实际：{data_count}条')

        # 统一的断言
        assert data_count <= 100  # GitHub最大限制

        if data_count>0:
            fields = ['id', 'name', 'full_name', 'html_url', 'fork', 'url']
            for fork_repo in response.json():
                for field in fields:
                    assert field in fork_repo
                assert fork_repo['fork'] == True
                assert 'login' in fork_repo['owner']

class TestForkWithOwnerRepo:

    @pytest.mark.parametrize('owner,repo,expected_code', [
        #owner的验证
        ('facebook', 'react', 200),
        ('luciawang057-sudo', 'react', 404),
        (None, 'react', 404),
        ('', 'react', 404),
        (' ', 'react', 404),
        ('no_exist_owner123', 'react', 404),
        #repo验证
        ('facebook',None,404),
        ('facebook','',404),
        ('facebook', ' ', 404),
        ('facebook', 'no_exist_repo1234', 404),
        #双重
        ('no_exist_owner123', 'no_exist_repo1234', 404),
        #特殊字符
        ('facebook', 'react@#$', 404),
        ('facebook', 'react  ', 404)

    ])
    def test_fork_with_owner_repo(self,github_client,owner,repo,expected_code):
        try:
            response=github_client.get(f'/repos/{owner}/{repo}/forks')
            if expected_code==200:
               assert_fork_success(response,None)

        except Exception as e:
            assert_fork_failure(e,expected_code,github_client)











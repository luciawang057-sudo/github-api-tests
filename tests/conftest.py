#tests/conftest.py
import os

import pytest
import random
import time
from pathlib import Path


from utils.github_client import GithubClient
from logging_config import set_up_logging# 导入函数
set_up_logging()# 调用函数执行日志配置



# def get_token_from_env():
#     try:
#         env_path=r'D:\Python学习\github\.env'
#         print(f"🔍 在conftest中查找文件: {env_path}")
#
#         with open(env_path, 'r') as f:
#             content = f.read()
#             print(f"📄 文件内容: {content}")
#
#             for line in content.split('\n'):
#                 if 'GITHUB_TOKEN='in line:
#                     token= line.replace('GITHUB_TOKEN=', '').strip()
#                     print(f"🔑 Token内容: {token}")
#                     return token
#
#
#         print("❌ 循环结束也没找到token")
#
#     except FileNotFoundError:
#         print(f'文件未找到{env_path}')
#     except Exception as e:
#         print(f'💥 conftest中其他错误: {e}')
#     return None
def get_token_from_env():
    try:
        token = os.getenv("API_TOKEN")
        if token:
            print(f"🔑 从环境变量获取 token，前5位: {token[:5]}...")
            return token
        #pathlib构建路径，从当前文件所在的目录开始找
        current_dir=Path(__file__)# conftest.py 的路径,获取当前文件的路径
        tests_dir=current_dir.parent#tests目录
        project_dir=tests_dir.parent#项目目录
        env_file=project_dir / ".env"

        if env_file.exists():
            with open(env_file,'r', encoding='utf-8') as f:
                content = f.read()
                print(f"📄 文件内容: {content}")
                for line in content.splitlines():
                    if line.startswith("API_TOKEN"):
                        token= line.replace('API_TOKEN=', '').strip()
                        print(f"🔑 从环境变量获取 token，前5位: {token[:5]}...")
                        return token
                print("❌ 循环结束也没找到token")
    except Exception as e:
        print(f'💥 错误: {e}')

    return None


@pytest.fixture(scope="session")
def github_client():
    token = get_token_from_env()

    client = GithubClient(token)
    yield client
    client.session.close()

@pytest.fixture
def get_filename():
        timestamp=int(time.time()*1000)
        random_suffix=random.randint(1000,9999)
        return f'test_{random_suffix}_{timestamp}.txt'

@pytest.fixture
def get_committer():
    return {
        'name': 'test_committer',
        'email': 'test_committer@qq.com',
        'date':'2025-10-05T00:00:00Z'
    }

@pytest.fixture
def get_author():
    return {
        'name': 'test_author',
        'email': 'test_author@qq.com',
        'date':'2025-10-05T00:00:00Z'

    }
@pytest.fixture
def get_sha(github_client,get_committer,get_author):
    timestamp=int(time.time()*1000)
    random_suffix=random.randint(1000,9999)
    filename = f'wyx_test_{random_suffix}_{timestamp}.txt'
    json_data={
        'message':'test_message',
        'content':'JXU5NjhGJXU0RkJGJXU1MTk5JXU1MTk5',
        'author':get_author,
        'committer':get_committer

    }
    response=github_client.put(f'/repos/luciawang057-sudo/github-api-tests/contents/{filename}',json=json_data)
    sha=response.json()['content']['sha']
    return {
        'sha': sha,
        'filename': filename,
    }

@pytest.fixture
def get_rulesets_id(github_client):
    all_rulesets = github_client.get('/repos/github/docs/rulesets')
    assert all_rulesets.status_code == 200
    assert isinstance(all_rulesets.json(), list)
    if not all_rulesets.json():
        pytest.skip("没有可用的规则集")
    ruleset_id = all_rulesets.json()[0]['id']
    return ruleset_id

@pytest.fixture(scope="function", autouse=True)  # 改为function作用域
def factory_fixture_with_update_ruleset(github_client,auto_clean_ruleset):
    """工厂fixture - 返回一个创建函数"""

    def _create_function(
            name='name',
            target='branch',
            enforcement='active',
            bypass_actors=None,
            conditions=None,
            rules=None

    ):
        """
        工厂函数 - 根据参数创建不同的测试数据
        """
        # 1. 根据参数构建数据
        data = {
            'name': name or f'test_wyx_{random.randint(1000,9999)}',
            'target':target,
            'enforcement':enforcement,          # ...
        }
        if bypass_actors is not None:
            data['bypass_actors']=bypass_actors
        if conditions is not None:
            data['conditions']=conditions
        if rules is not None:
            data['rules']=rules
        # 2. 调用API创建资源
        response = github_client.post('/repos/luciawang057-sudo/github-api-tests/rulesets',json=data)
        # 3. 提取返回的ID或数据
        resource_id = response.json()['id']
        # 4. 可选：添加到清理列表
        auto_clean_ruleset.append(resource_id)
        # 5. 返回创建的资源
        return resource_id  # 或者返回整个响应对象
    # 返回工厂函数
    return _create_function




@pytest.fixture(scope='session')
def auto_clean_ruleset(github_client):
    create_ruleset=[]# 创建空列表
    yield create_ruleset# 把这个列表传给测试函数
    try:
        for ruleset_id in create_ruleset:
            all_rulesets = github_client.delete(f'/repos/luciawang057-sudo/github-api-tests/rulesets/{ruleset_id}')
            assert all_rulesets.status_code == 204
            print(f'清理成功，{ruleset_id}')
    except Exception as e:
        github_client.logger.error(f'清理{ruleset_id},出错{e}')


@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests(github_client):
    """测试结束后清理所有创建的资源"""
    yield
    # 测试结束后执行清理
    print("🧹 开始清理测试资源...")

    # 1. 清理测试文件
    try:
        # 获取并删除所有以 test_ 开头的文件
        contents = github_client.get('/repos/luciawang057-sudo/github-api-tests/contents')
        for item in contents.json():
            if isinstance(item, dict) and item.get('name', '').startswith(('test_', 'wyx_test_')):
                delete_data = {
                    'message': 'Cleanup test file',
                    'sha': item['sha']
                }
                github_client.delete(
                    f'/repos/luciawang057-sudo/github-api-tests/contents/{item["name"]}',
                    json=delete_data
                )
                print(f"🗑️ 已删除测试文件: {item['name']}")
    except Exception as e:
        print(f"⚠️ 清理文件时出错: {e}")



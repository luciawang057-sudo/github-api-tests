#tests/conftest.py
import os

import pytest
import random
import time
from pathlib import Path


from utils.github_client import GithubClient



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
        current_dir=Path(__file__)# conftest.py 的路径
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


@pytest.fixture
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
    if not all_rulesets:
        pytest.skip("没有可用的规则集")
    ruleset_id = all_rulesets.json()[0]['id']
    return ruleset_id

@pytest.fixture
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




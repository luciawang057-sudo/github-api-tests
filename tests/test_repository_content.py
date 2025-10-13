import pytest

import pytest


class TestRepoContent:

    @pytest.mark.parametrize('owner,repo,path,expected_status_code', [
        # 正常文件路径 - 期望200
        ('octocat', 'Spoon-Knife', "README.md", 200),
        ('microsoft', 'vscode', 'README.md', 200),
        ('facebook', 'react', 'README.md', 200),

        # 不存在的路径 - 期望404
        ('octocat', 'Spoon-Knife', "src/", 404),
        ('octocat', 'Spoon-Knife', ".github/workflows/ci.yml", 404),
        ('octocat', 'Spoon-Knife', "no_exist_path", 404),

        # 特殊路径测试（使用占位符避免pytest显示问题）
        ('octocat', 'Spoon-Knife',None, 404),  # None路径
        ('octocat', 'Spoon-Knife', "", 200),  # 空路径（获取根目录）
        ('octocat', 'Spoon-Knife', " ", 404),  # 空格路径

        # 不存在的仓库 - 期望404
        ('octocat', 'test_repo', "README.md", 404),
        ('octocat', "no_exist_repo ", "README.md", 404),

        # 特殊owner/repo测试
        ('octocat', None, "README.md", 404),
        ('octocat', "", "README.md", 404),
        ('octocat', " ", "README.md", 404),
        (None, 'Spoon-Knife', "README.md", 404),
        ('', 'Spoon-Knife', "README.md", 404),
        (' ', 'Spoon-Knife', "README.md", 404),

        # 不存在的用户和超长参数 - 期望404
        ('no_exist_users9999', 'Spoon-Knife', "README.md", 404),
        ('wyxlucia' * 50, 'Spoon-Knife', "README.md", 404),
        ('octocat', 'Spoon-Knife' * 50, "README.md", 404),
    ])
    def test_get_repository_content(self, github_client, owner, repo, path, expected_status_code):
        print(f"测试用例: owner={owner}, repo={repo}, path='{path}', expected={expected_status_code}")



        if expected_status_code == 200:
            # 期望200 - 正常请求并验证响应
            response = github_client.get(f'/repos/{owner}/{repo}/contents/{path}')
            assert response.status_code == expected_status_code
            response_data = response.json()
            print(f"状态码: {response.status_code}")
            print(f'正确响应体：{response_data}')

            if isinstance(response_data, dict):
                # 单个文件 - 验证包含所有必要字段
                assert len(response_data) > 0
                required_fields = ['type', 'encoding', 'size', 'name', 'path', 'content',
                                   'url', 'git_url', 'html_url', 'download_url']
                for field in required_fields:
                    assert field in response_data
            elif isinstance(response_data, list):
                # 目录路径 - 验证列表项结构
                assert len(response_data) > 0
                for item in response_data:
                    assert isinstance(item, dict)
                    assert 'html_url' in item
                    assert 'download_url' in item

        else:
            # 期望404 - 验证会抛出异常
            with pytest.raises(Exception) as exc_info:
                github_client.get(f'/repos/{owner}/{repo}/contents/{path}')

            # 验证异常中的状态码和错误信息
            assert hasattr(exc_info.value, 'response')
            assert exc_info.value.response.status_code == expected_status_code

            error_data = exc_info.value.response.json()
            print(f"状态码: {exc_info.value.response.status_code}")
            print(f"错误体: {error_data}")

            # 验证错误信息结构
            assert 'message' in error_data
            assert 'Not Found' in error_data['message']
            github_client.logger.info(f'预期错误{error_data}')
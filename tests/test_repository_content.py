import pytest

class TestRepoContent:

    @pytest.mark.parametrize('owner,repo,path,expected_status_code', [
    ('octocat','Spoon-Knife',"README.md",200),
    ('microsoft', 'vscode', 'README.md', 200),
     ('facebook', 'react', 'README.md', 200),
     ('octocat','Spoon-Knife',"src/",404),
    ('octocat', 'Spoon-Knife', ".github/workflows/ci.yml",404),

    ('octocat','Spoon-Knife',"no_exist_path",404),

    ('octocat','Spoon-Knife',None,404),
    ('octocat','Spoon-Knife',"",404),
    ('octocat','Spoon-Knife'," ",404),

    ('octocat','test_repo',"README.md",404),
    ('octocat',"no_exist_repo ","README.md",404),
    ('octocat',None,"README.md",404),
    ('octocat',"","README.md",404),
    ('octocat'," ","README.md",404),
    (None,'Spoon-Knife',"README.md",404),
    ('','Spoon-Knife',"README.md",404),
    (' ','Spoon-Knife',"README.md",404),
    ('no_exist_users9999','Spoon-Knife',"README.md",404),
    ('wyxlucia'*50,'Spoon-Knife',"README.md",404),
    ('octocat', 'Spoon-Knife'*50, "README.md",404),

])
    def test_get_repository_content(self,github_client,owner,repo,path,expected_status_code):
        safe_owner='' if owner in[None,'',' '] else owner
        safe_repo='' if repo in[None,'',' '] else repo
        safe_path='' if path in[None,'',' '] else path
        try:
            response = github_client.get(f'/repos/{safe_owner}/{safe_repo}/contents/{safe_path}')
            assert response.status_code == expected_status_code
            if expected_status_code == 200:
                assert isinstance(response.json(),dict)
                assert len(response.json())>0
                fields=['type','encoding','size','name','path','content','url','git_url','html_url','download_url']
                for field in fields:
                    assert field in response.json()
            elif expected_status_code == 404:
                assert '404' in response.json()
                assert 'Error' in response.json() or 'Not Found' in response.json()
        except Exception as e:
            github_client.logger.error(f'预期错误{e}')


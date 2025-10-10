
import pytest



# class TestGetRepositoryRuleset:
#
#     @pytest.mark.smoke
#     def test_all_repository_rulesets_smoke(self,github_client):
#        responses=github_client.get('/repos/github/docs/rulesets')
#        assert responses.status_code == 200
#        print(f'响应体信息：{responses.json()}')
#        assert isinstance(responses.json(),list)
#        fields=[('id',int),('name',str),('target',str),('source',str),('source_type',str),('enforcement',str),('node_id',str),('_links',dict),('created_at',str),('updated_at',str),('updated_at',str)]
#        for response in responses.json():
#            for field,expect_type in fields:
#                assert field in response
#                assert isinstance(response[field],expect_type)
#            assert response['id']>0
#            assert response['name']!=''
#            assert response['target'] in['branch','tag','push']
#            assert len(response['name'])>0
#            assert len(response['target'])>0
#            assert len(response['source'])>0
#            assert len(response['source_type'])>0
#            assert len(response['enforcement'])>0
#            assert len(response['node_id'])>0
#            assert len(response['_links'])>0
#            assert isinstance(response['_links']['self'],dict)
#            assert isinstance(response['_links']['html'],dict)
#            assert len(response['created_at'])>0
#            assert isinstance(response['created_at'],str)
#            assert len(response['updated_at'])>0
#            assert isinstance(response['updated_at'],str)
#
#     def test_get_a_repository_rulesets_smoke(self,github_client):
#         rulesets_response=github_client.get('/repos/github/docs/rulesets')
#         assert rulesets_response.status_code == 200
#         all_rulesets=rulesets_response.json()
#         ruleset_id=all_rulesets[0]['id']
#
#         response=github_client.get(f'/repos/github/docs/rulesets/{ruleset_id}')
#         assert response.status_code == 200
#         print(f'响应体信息：{response.json()}')
#         assert isinstance(response.json(),dict)
#         fields = [('id', int), ('name', str), ('target', str), ('source', str), ('source_type', str),
#                  ('enforcement', str), ('conditions', dict), ('rules', list), ('node_id', str),('created_at', str), ('updated_at', str),
#                  ('_links', dict)
#                  ]
#         for field,expected_type in fields:
#             assert field in response.json()
#             assert isinstance(response.json()[field],expected_type)
#         assert response.json()['id'] == ruleset_id
#         assert response.json()['name'] !=''
#         assert response.json()['target'] !=''
#         assert response.json()['source_type']!=''
#         assert response.json()['source']!=''
#         assert response.json()['enforcement']!=''
# class TestRepositoryRulesetSuccess:
#     @pytest.mark.parametrize('per_page,page,includes_parents,targets,expected_code',[
#         (30, 1, True, 'branch', 200),
#         (100, 1, True, 'branch', 200),
#         (50, 1, True, 'tag', 200),
#         (50, 1, True, 'push', 200),
#         (30, 1, False, 'branch', 200),
#         (100, 1, False, 'branch', 200),
#         (50, 1, False, 'tag', 200),
#         (50, 1, False, 'push', 200)
#                              ]
#
#     )
#     def test_get_Repository_Rulesetcases(self, github_client,per_page,page,includes_parents,targets,expected_code,
#                                          ):
#         params={
#             'per_page':per_page,
#             'page':page,
#             'includes_parents': includes_parents,
#             'targets':targets
#
#         }
#         response=github_client.get('/repos/github/docs/rulesets',params=params)
#         assert response.status_code == expected_code
#         response_data=response.json()
#         assert isinstance(response_data,list)
#
#         if response_data != []:
#             for item in response_data:
#                 assert item['target']==targets
#                 fields = [('id', int), ('name', str), ('target', str), ('source', str), ('source_type', str),
#                                            ('enforcement', str), ('node_id', str),('created_at', str), ('updated_at', str),
#                                            ('_links', dict)
#                                            ]
#                 for field, expected_type in fields:
#                     assert field in item
#                     assert isinstance(item[field], expected_type)
#                     assert item['id']>0
#                     assert item['name']!='' and  len(item['name'])>0
#                     assert item['source_type'] !='' and item['source_type'] in ('Organization', 'Repository')
#             assert len(response_data) <= per_page
#         print(f'响应体信息：{response.json()}')

# class TestRepositoryRulesetConflict:
#     @pytest.mark.parametrize('owner,repo,targets,expected_code', [
#         ('luciawang057-sudo','docs',None,404),
#         ('github','luciawang057-sudo',None,404),
#         ('github','docs','luciawang057-sudo',422),
#
#     ])
#     def test_get_allrepository_ruleset_with_wrong_cases(self,github_client,owner,repo,targets,expected_code):
#         params={'targets':targets}
#         with pytest.raises(Exception) as e:
#            github_client.get(f'/repos/{owner}/{repo}/rulesets',params=params)
#         assert hasattr(e.value, 'response')
#         assert expected_code == e.value.response.status_code
#         assert e.value.response.status_code in [404, 422]
#
#         error_data=e.value.response.json()
#         print(f'错误响应体：{error_data}')
#         assert 'message' in error_data
#         assert 'status' in error_data
#         assert error_data['status'] == str(expected_code)
#         if expected_code == 404:
#             assert error_data['message']=='Not Found'
#         elif expected_code == 422:
#             assert 'Invalid target found' in error_data['message']
#
#
#
#
#     @pytest.mark.parametrize('owner,repo,rulesets_id,expected_code', [
#         ('luciawang057-sudo','docs','invalid',404),
#         ('github','luciawang057-sudo','invalid',404),
#         ('github','docs','no_exist_rulesets_id',404),
#     ])
#     def test_get_a_repository_ruleset_with_wrong_cases(self,github_client,owner,repo,rulesets_id,expected_code,get_rulesets_id):
#         if rulesets_id == 'invalid':
#             rulesets_id = get_rulesets_id
#         else:
#             rulesets_id = rulesets_id
#         with pytest.raises(Exception) as e:
#             github_client.get(f'/repos/{owner}/{repo}/rulesets/{rulesets_id}')
#         assert hasattr(e.value, 'response')
#         assert expected_code == e.value.response.status_code
#
#         error_data=e.value.response.json()
#         print(f'错误响应体：{error_data}')
#         assert 'message' in error_data
#         assert 'status' in error_data
#         assert error_data['status'] == str(expected_code)
#         assert error_data['message'] == 'Not Found'

class TestRepositoryRulesetBoundary:
    # @pytest.mark.parametrize('owner,repo,,expected_code', [
    #     ('git   hub','docs',404),
    #     (None,'docs',404),
    #     ('','docs',404),
    #     (' ','docs',404),
    #     ('github$^*123','docs', 404),
    #     ('no_exist_owner','docs',404),
    #     ('github','do    cs',404),
    #     ('github','None',404),
    #     ('github','',404),
    #     ('github',' ',404),
    #     ('github','docs$^*123',404),
    #     ('github','DOCX',404),
    #     ('github','no_exist_repo',404)
    #
    #
    #
    # ])
    # def test_get_all_boundary_owner_repo(self,github_client,owner,repo,expected_code):
    #     with pytest.raises(Exception) as e:
    #         github_client.get(f'/repos/{owner}/{repo}/rulesets')
    #     assert hasattr(e.value, 'response')
    #     assert expected_code == e.value.response.status_code
    #     error_data = e.value.response.json()
    #     print(f'错误消息体{error_data}')
    #     assert 'message' in error_data
    #     assert 'status' in error_data
    #     assert error_data['status'] == str(expected_code)
    #     assert error_data['message'] == 'Not Found'


    @pytest.mark.parametrize('per_page,page', [
        #per_page边界
        (30,1),(0,1),(1,1),(50,1),(100,1),(101,1),(30,-1),(99999999,1),(None,1),('',1),('  ',1),('30',1),
        #page边界
        (30,0),(30,999999),(30,-1),(30,30),(30,None),(30,''),(30,' '),(30,'1'),
        #双重
        (None,None)

    ])
    def test_get_all_boundary_page_per_page(self,github_client, per_page, page):
        params={'per_page':per_page,'page':page}
        # if per_page is not None:
        #     params['per_page'] = per_page
        # if page is not None:
        #     params['page'] = page
        responses=github_client.get('/repos/github/docs/rulesets', params=params)
        assert responses.status_code == 200
        responses_data = responses.json()
        data_count = len(responses_data)
        assert isinstance(responses_data, list)

        if per_page is None:
            print(f'默认分页是30，数量为{data_count}')
        elif isinstance(per_page, int) and 1<=per_page<=100:
            print(f'分页是{per_page}，数量为{data_count}')
        elif isinstance(per_page, int) and per_page>100:
            print(f'分页是100，数量为{data_count}')
        else:
            print(f'无效分页，默认分页是30，数量为{data_count}')

        assert data_count <= 100

        if data_count >0:

            for response in responses_data:
                assert isinstance(response, dict)
                fields = [('id', int), ('name', str), ('target', str), ('source', str), ('source_type', str),
                             ('enforcement', str),('node_id', str),('created_at', str), ('updated_at', str),
                             ('_links', dict)
                             ]
                for field,expected_type in fields:
                    assert field in response
                    assert isinstance(response[field], expected_type)
                    assert response['id'] > 0
                    assert response['name']!='' and  len(response['name'])>0
                    assert response['source_type'] !='' and response['source_type'] in ('Organization', 'Repository')

















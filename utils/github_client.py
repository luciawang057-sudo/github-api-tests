#utils/github_client.py

from config.setting import BASE_URL,API_VERSION,TIMEOUT
import requests
import logging
class GithubClient:
    def __init__(self,token):
        self.session = requests.Session()
        self.BASE_URL = BASE_URL
        self.API_VERSION = API_VERSION
        self.TIMEOUT = TIMEOUT
        self.token = token
        self.logger = logging.getLogger(__name__)

        # 添加调试
        print(f"🔧 GithubClient接收到的token: {token}")

        #https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version':API_VERSION,
            'Authorization': f'Bearer {self.token}',
            'User-Agent': 'Awesome-Octocat-App'
        }
        if self.token is not None:
            print(f"📋 设置的请求头: {headers}")
            self.session.headers.update(headers)

    def _request(self,method,endpoint,**kwargs):
        url=f'{self.BASE_URL.rstrip("/")}/{endpoint.lstrip("/")}'
        self.logger.info(f'请求方法：{method.upper()},{url}')
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.TIMEOUT
        try:
            response=self.session.request(method,url,**kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(e)
            raise
    def get(self,endpoint,**kwargs):
        return self._request('get',endpoint,**kwargs)
    def post(self,endpoint,**kwargs):
        return self._request('post',endpoint,**kwargs)
    def put(self,endpoint,**kwargs):
        return self._request('put',endpoint,**kwargs)
    def delete(self,endpoint,**kwargs):
        return self._request('delete',endpoint,**kwargs)
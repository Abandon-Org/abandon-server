import json
import time
from urllib.parse import urlencode

import aiohttp
from aiohttp import FormData
from fastapi import Body


class AsyncRequest(object):

    def __init__(self, url: str, timeout=15, **kwargs):
        self.url = url
        self.kwargs = kwargs
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    def get_cookie(self, session):
        cookies = session.cookie_jar.filter_cookies(self.url)
        return {k: v.value for k, v in cookies.items()}

    def get_data(self, kwargs):
        if kwargs.get("json") is not None:
            return kwargs.get("json")
        return kwargs.get("data")

    async def invoke(self, method: str):
        start = time.time()
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
            async with session.request(method, self.url, timeout=self.timeout, **self.kwargs) as resp:
                if resp.status != 200:
                    # 修复bug，当http状态码不为200的时候给出提示
                    return await self.collect(False, self.get_data(self.kwargs), resp.status, msg="http状态码不为200")
                cost = "%.0fms" % ((time.time() - start) * 1000)
                response, json_format = await AsyncRequest.get_resp(resp)
                cookie = self.get_cookie(session)
                return await self.collect(True, self.get_data(self.kwargs), resp.status, response,
                                          resp.headers, resp.request_info.headers, elapsed=cost,
                                          cookies=cookie, json_format=json_format)

    async def download(self):
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True)) as session:
            async with session.request("GET", self.url, timeout=self.timeout, **self.kwargs) as resp:
                if resp.status != 200:
                    raise Exception("download file failed")
                return await resp.content.read()

    @staticmethod
    async def client(url: str, timeout=15, **kwargs):
        if not url.startswith(("http://", "https://")):
            raise Exception("请输入正确的url, 记得带上http哦")
        headers = kwargs.get("headers")
        body = kwargs.get("body", {})
        if body is None:
            r = AsyncRequest(url, headers=headers, timeout=timeout)
        elif body["body_type"] == "none":
            r = AsyncRequest(url, headers=headers, timeout=timeout)
        elif body["body_type"] == "json":
            if "Content-Type" not in headers:
                headers['Content-Type'] = "application/json; charset=UTF-8"
            try:
                body_data = body["body"]
                body_data = json.loads(json.dumps(body_data))
            except json.JSONDecodeError as e:
                raise Exception(f"json格式不正确: {e}")
            r = AsyncRequest(url, headers=headers, timeout=timeout,
                             json=body_data)
            # # 判断body类型是否为formdata
            # if body and isinstance(body, dict) and body.get("body_type") == "formdata":
            #     try:
            #         form_data = FormData()
            #         items = body.get("body", [])
            #         for item in items:
            #             # 如果是文本类型，直接添加key-value
            #             if item.get("type") == 'TEXT':
            #                 form_data.add_field(item.get("key"), item.get("value", ''))
            #             else:
            #                 # 其他类型处理方式，你可以根据需要进行修改
            #                 pass
            #         r = await AsyncRequest(method, url, headers=headers, data=form_data, timeout=timeout)
            #     except Exception as e:
            #         raise Exception(f"解析form-data失败: {str(e)}")
        elif body["body_type"] == "formdata":
            try:
                body_data = body.get("body", [])
                form_data = FormData()
                for item in body_data:
                    # 如果是文本类型，直接添加key-value
                    if item.get("type") == 'TEXT':
                        form_data.add_field(item.get("key"), item.get("value", ''))
                    # todo 后期可能会改写add_file方法，暂时先注释掉基础写法
                    # else:
                    #     # 如果是文件类型，使用add_file方法添加文件
                    #     file_content = await file.read()
                    #     form_data.add_file(item.get("key"), file_content, filename=item.get("value"))
                r = AsyncRequest(url, headers=headers, data=form_data, timeout=timeout)
            except Exception as e:
                raise Exception(f"解析form-data失败: {str(e)}")
        elif body["body_type"] == "xform":
            body_data = kwargs.get("body", "{}")
            body_encoded = urlencode(body_data)
            r = AsyncRequest(url, headers=headers, data=body_encoded, timeout=timeout)
        else:
            # 暂时未支持其他类型
            r = AsyncRequest(url, headers=headers, timeout=timeout, data=kwargs.get("body", {})["body"])
        return r

    @staticmethod
    async def get_resp(resp):
        try:
            data = await resp.json(encoding='utf-8')
            # 说明是json格式
            return json.dumps(data, ensure_ascii=False, indent=4), True
        except:
            data = await resp.text()
            # 说明不是json格式，我们不做loads操作了
            return data, False

    @staticmethod
    def get_request_data(body):
        request_body = body
        if isinstance(body, bytes):
            request_body = request_body.decode()
        if isinstance(body, FormData):
            request_body = str(body)
        if isinstance(request_body, str) or request_body is None:
            return request_body
        return json.dumps(request_body, ensure_ascii=False, indent=4)

    @staticmethod
    async def collect(status, request_data, status_code=200, response=None, response_headers=None,
                      request_headers=None, cookies=None, elapsed=None, msg="success", **kwargs):
        """
        收集http返回数据
        :param status: 请求状态
        :param request_data: 请求入参
        :param status_code: 状态码
        :param response: 相应
        :param response_headers: 返回header
        :param request_headers:  请求header
        :param cookies:  cookie
        :param elapsed: 耗时
        :param msg: 报错信息
        :return:
        """
        request_headers = json.dumps({k: v for k, v in request_headers.items()} if request_headers is not None else {},
                                     ensure_ascii=False)
        response_headers = json.dumps(
            {k: v for k, v in response_headers.items()} if response_headers is not None else {},
            ensure_ascii=False)
        cookies = {k: v for k, v in cookies.items()} if cookies is not None else {}
        cookies = json.dumps(cookies, ensure_ascii=False)
        return {
            "status": status, "response": response, "status_code": status_code,
            "request_data": AsyncRequest.get_request_data(request_data),
            "response_headers": response_headers, "request_headers": request_headers,
            "msg": msg, "time": elapsed, "cookies": cookies, **kwargs,
        }

from fastapi import APIRouter

from src.app.customized.customized_response import AbandonJSONResponse
from src.app.requestpage.AsyncHttpClient import AsyncRequest
from src.app.schema.http import HttpRequestForm

router = APIRouter(prefix="/request")


@router.post("/http")
async def http_request(data: HttpRequestForm):
    try:
        r = await AsyncRequest.client(data.url, headers=data.headers, body=data.body)
        response = await r.invoke(data.method)
        return AbandonJSONResponse.success(response)
    except Exception as e:
        return AbandonJSONResponse.failed(e)
    # try:
    #     r = await AsyncRequest.client(data.url, data.body_type, headers=data.headers, body=data.body)
    #     response = await r.invoke(data.method)
    #     if response.get("status"):
    #         return PityResponse.success(response)
    #     return PityResponse.failed(response.get("msg"), data=response)
    # except Exception as e:
    #     return PityResponse.failed(e)

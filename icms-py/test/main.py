# filename: main.py
from fastapi import FastAPI, Body # 导入 Body
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse # 导入 PlainTextResponse

app = FastAPI()

class StringRequest(BaseModel):
    text: str

class StringResponse(BaseModel):
    reversed_text: str

@app.post("/reverse", response_class=PlainTextResponse) # <-- 关键：指定响应类型为纯文本
async def reverse_string(text_to_reverse: str = Body(..., media_type="text/plain")): # <-- 关键：直接接收纯文本请求体
    """
    接收一个纯字符串并返回其反转后的版本。
    """
    print(f"FastAPI received raw string: {text_to_reverse}")
    reversed_str = text_to_reverse[::-1]
    print(f"FastAPI sending back raw string: {reversed_str}")
    return reversed_str # <-- 直接返回字符串
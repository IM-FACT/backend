from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/im-fact/ask")
async def ask_factcheck(req: Request):
    request=await req.json()
    quest=request.get("content")

    if not quest:
        return JSONResponse(
            status_code=400,
            content={"error": "질문이 존재하지 않음."}
        )

    # 답변 생성 로직
    # ans=factcheck(quest)

    ans=f"'{quest}'에 대한 테스트 응답입니다."

    return JSONResponse(
        status_code=200,
        content={"content": ans}
    )
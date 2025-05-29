from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import traceback

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.post("/im-fact/ask")
async def ask_factcheck(req: Request):
    try:
        request = await req.json()
        quest = request.get("content")

        if not quest:
            return JSONResponse(
                status_code=400,
                content={"error": "질문이 존재하지 않음."}
            )

        # 더미 응답 반환
        ans = f"'{quest}'에 대한 테스트 응답입니다."

        return JSONResponse(
            status_code=200,
            content={"content": ans}
        )
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"서버 오류: {str(e)}"}
        ) 
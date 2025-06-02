from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import traceback

# asyncio 임포트 추가
import asyncio

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

        # main.py에서 전역 processor 인스턴스 가져오기
        import main
        if main.processor is None:
            return JSONResponse(
                status_code=500,
                content={"error": "MainProcessor가 초기화되지 않았습니다."}
            )

        # 비동기 처리를 위해 별도 스레드에서 실행
        result = await asyncio.to_thread(main.processor.process, quest)
        
        if result["success"]:
            ans = result["final_answer"]
        else:
            ans = f"처리 오류: {result['message']}"

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
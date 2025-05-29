from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from langchain.main_processor import MainProcessor
import traceback

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}

processor = MainProcessor()

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

        result = processor.process(quest)

        if result["success"]:
            if result["operation"] == "found_similar":
                best_ans = result["similar_items"][0]
                ans = best_ans["text"]
            elif result["operation"] == "saved_new":
                ans = "새로운 질문 등록"
            else:
                ans = "처리 불명확"
        else:
            ans = "처리 오류"

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
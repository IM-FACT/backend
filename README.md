# IM.FACT Backend - FastAPI

IM.FACT 서비스의 백엔드 라우팅을 담당합니다.  
사용자의 질문을 입력받아 응답을 생성하는 구조로 작동합니다.

## Endpoint
`POST /im-fact/ask`

---

## Request Body (JSON)

```json
{
  "content": "전기차는 친환경인가요?"
}
```

---

## Response Body (JSON)

```json
{
  "content": "'전기차는 친환경인가요?'에 대한 테스트 응답입니다."
}
```

---

## 상태 코드
- 200 :요청이 성공적으로 처리되어 응답이 반환됨
- 400 :요청 JSON에 `"content"` 필드가 누락됨

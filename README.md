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
  "content": "전기차는 주행 시 배출가스가 없어 친환경 차량으로 간주되지만, 전체 생애 주기에서는 다양한 요인을 고려해야 합니다.
  
  국제에너지기구(IEA)의 2021년 보고서에 따르면, ..."
}
```

---

## 상태 코드
- 200 :요청이 성공적으로 처리되어 응답이 반환됨
- 400 :요청 JSON에 `"content"` 필드가 누락됨
- 500 :서버 오류

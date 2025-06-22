from openai import OpenAI
import os
from app.config import settings
import json
from typing import List, Dict
import re

client = OpenAI(api_key=settings.openai_api_key)

def load_prompt(filename):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompts_dir = os.path.join(root_dir, "prompts")
    filepath = os.path.join(prompts_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

# GPT-4.1을 사용하여 MCP 수집 문서 기반 질문 답변 생성
def ans_with_mcp(query: str, docs: List[Dict[str, str]]) -> Dict:
    try:
        action_prompt = load_prompt("generate_ans_prompt.txt")
        # 제목 정보도 프롬프트에 포함
        pool = "\n\n".join(f"[출처 제목] {doc.get('title', '제목 없음')}\n[출처 URL] {doc['url']}\n[내용] {doc['content']}" for doc in docs)

        user_prompt = f"""{action_prompt}
                        [문서 정보] {pool}
                        [질문] {query} """

        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[
                {"role": "system", "content": action_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0,
        )
        
        answer = response.choices[0].message.content.strip()
        
        # 답변 끝에 있는 URL 목록을 확실하게 제거 (개선된 로직)
        lines = answer.strip().split('\n')
        url_pattern = re.compile(r'^\s*\[?\d+\]?\.?\s*https?://\S+')
        
        # URL 패턴이 아닌 마지막 줄의 인덱스를 찾음
        last_non_url_index = -1
        for i in range(len(lines) - 1, -1, -1):
            if not url_pattern.match(lines[i].strip()):
                last_non_url_index = i
                break
        
        # URL이 아닌 내용까지만 잘라내어 최종 답변으로 사용
        if last_non_url_index != -1:
            answer = '\n'.join(lines[:last_non_url_index + 1]).strip()

        # 출처 정보 재구성
        sources = [{"title": doc.get("title", "제목 없음"), "url": doc["url"]} for doc in docs]
        
        return {"answer": answer, "sources": sources}

    except Exception as e:
        print("GPT 4.1 답변 생성 실패")
        print(e)
        return {"answer": "답변 생성 실패", "sources": []}
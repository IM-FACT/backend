from openai import OpenAI
import os
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# 예시 문서 리스트
documents = [
    "전기차는 온실가스 배출을 줄입니다.",
    "국지성 호우는 이상기후 현상입니다.",
    "강아지는 귀엽다.",
    "강아지는 무섭다.",
    "강아지는 충성심이 강하며 귀엽다.",
    "전기차는 전기를 사용합니다.",
    "기후 변화는 전 세계적인 이슈입니다."
]

# 사용자 질문
query = "기후변화가 뭔가요?"
query_emb = get_embedding(query)

# 문서 임베딩
doc_embs = [get_embedding(doc) for doc in documents]

# 유사도 계산
sims = cosine_similarity([query_emb], doc_embs)[0]

# 결과 정리
df = pd.DataFrame({
    "document": documents,
    "similarity": sims
}).sort_values(by="similarity", ascending=False)

print(df)

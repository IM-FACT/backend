from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("intfloat/multilingual-e5-small")

query = "query: 전기차는 환경 보호에 도움이 되는가?"
documents = [
    "passage: 국지성 호우는 이상기후 현상이다.",
    "passage: 전기차는 친환경이다.",
    "passage: 강아지는 귀엽다.",
    "passage: 좁은 지역에 내리는 비는 국지성 호우로 분류됩니다.",
    "passage: 탄소중립은 기후 변화 대응에 필수적입니다."
]

query_emb = model.encode([query])
doc_embs = model.encode(documents)

sims = cosine_similarity(query_emb, doc_embs)[0]

print("\n[유사도 높은 순 정렬 결과]")
for doc, sim in sorted(zip(documents, sims), key=lambda x: x[1], reverse=True):
    print(f"유사도 {sim:.4f} → {doc.replace('passage: ', '')}")

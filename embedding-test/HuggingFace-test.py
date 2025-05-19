from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("intfloat/multilingual-e5-small")

query = "query: 좁은 지역에 내리는 비도 이상 기후 현상인가?"
doc = "passage: 강아지는 귀엽다."

query_emb = model.encode(query)
doc_emb = model.encode(doc)

sim = cosine_similarity([query_emb], [doc_emb])[0][0]
print(f"유사도: {sim:.4f}")
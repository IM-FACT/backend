# embedding_generator.py (LangChain 버전)
import sys
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from app.redis.redis_handler import EmbeddingsCacheHandler
from app.config import settings
import numpy as np


class EmbeddingGenerator:
    """LangChain을 사용하여 텍스트 임베딩을 생성하는 클래스 (리팩토링)"""

    def __init__(self, model_name: str = "text-embedding-3-small", redis_url: str = None):
        """
        임베딩 생성기 초기화

        Args:
            model_name (str): 사용할 OpenAI 임베딩 모델명
            redis_url (str): Redis 서버의 URL (None이면 config에서 가져옴)
        """
        try:
            # config에서 API 키 가져오기
            self.api_key = settings.openai_api_key
            if not self.api_key:
                print("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
                sys.exit(1)

            # Redis URL 설정 (매개변수가 없으면 config에서 가져옴)
            if redis_url is None:
                redis_url = settings.redis_url

            # 모델명 저장
            self.model_name = model_name

            # LangChain OpenAI 임베딩 모델 초기화
            self.embeddings = OpenAIEmbeddings(
                model=model_name,
                openai_api_key=self.api_key
            )

            # Redis 캐시 초기화
            self.cache = EmbeddingsCacheHandler(redis_url=redis_url)

            print(f"임베딩 생성기 초기화 완료: 모델 {model_name}")
            
        except Exception as e:
            print(f"임베딩 생성기 초기화 오류: {e}")
            sys.exit(1)

    def embed(self, text: str) -> Optional[List[float]]:
        """
        텍스트를 임베딩 벡터로 변환 (캐시 우선)
        Args:
            text (str): 임베딩할 텍스트
        Returns:
            Optional[List[float]]: 임베딩 벡터 (실패 시 None)
        """
        if not text or text.strip() == "":
            print("오류: 임베딩할 텍스트가 비어 있습니다.")
            return None
        try:
            # 1. 캐시 조회
            cached = self.cache.get_embedding(text)
            if cached is not None:
                return cached
            # 2. 임베딩 생성
            embedding = self.embeddings.embed_query(text)
            embedding_np = np.array(embedding, dtype=np.float32)
            # 3. 캐시에 저장
            self.cache.set_embedding(text, embedding_np)
            return embedding_np
        except Exception as e:
            print(f"임베딩 생성 오류: {e}")
            return None
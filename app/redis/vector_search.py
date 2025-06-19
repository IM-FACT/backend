# vector_search.py
"""
Redis 8의 Vector Search 기능을 활용한 벡터 검색 모듈
HNSW (Hierarchical Navigable Small World) 알고리즘을 사용하여 빠른 유사도 검색 구현
"""

import redis
from redis.commands.search.field import VectorField, TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import numpy as np
from typing import List, Dict, Any
from app.redis.debug_utils import RedisIndexDebugger



class VectorSearchIndex:
    """Redis Vector Search를 위한 인덱스 관리 클래스"""
    
    def __init__(self, 
                 redis_client: redis.Redis,
                 index_name: str = "climate_vectors",
                 vector_dimension: int = 1536,
                 distance_metric: str = "COSINE"):
        """
        Vector Search 인덱스 초기화
        
        Args:
            redis_client: Redis 클라이언트 인스턴스
            index_name: 인덱스 이름
            vector_dimension: 벡터 차원 (OpenAI text-embedding-3-small은 1536)
            distance_metric: 거리 측정 방식 (COSINE, L2, IP)
        """
        self.redis_client = redis_client
        self.index_name = index_name
        self.vector_dimension = vector_dimension
        self.distance_metric = distance_metric
        
        # 디버깅 유틸리티 초기화
        self.debugger = RedisIndexDebugger(redis_client)
        
        # 인덱스 생성 또는 확인
        self._ensure_index_exists()
        
    def _ensure_index_exists(self):
        """인덱스가 존재하는지 확인하고, 없으면 생성"""
        print(f"\n🔍 인덱스 '{self.index_name}' 상태 확인 중...")
        
        # 상세 진단 실행
        exists = self.debugger.check_index_exists(self.index_name)
        
        if exists:
            doc_count = self.debugger.count_documents_in_index(self.index_name)
            print(f"✅ 인덱스 '{self.index_name}' 존재 ({doc_count}개 문서)")
        else:
            # 인덱스가 없으면 생성
            print(f"🔧 인덱스 '{self.index_name}' 생성 중...")
            self._create_index()
            
            # 생성 후 다시 확인
            if self.debugger.check_index_exists(self.index_name):
                print(f"✅ 인덱스 '{self.index_name}' 생성 완료")
            else:
                print(f"❌ 인덱스 '{self.index_name}' 생성 실패!")
            
    def _create_index(self):
        """Vector Search 인덱스 생성"""
        try:
            # 인덱스 스키마 정의
            schema = (
                # 벡터 필드 - HNSW 알고리즘 사용
                VectorField("embedding_vector",
                    "HNSW",  # 알고리즘 
                    {
                        "TYPE": "FLOAT32",
                        "DIM": self.vector_dimension,
                        "DISTANCE_METRIC": self.distance_metric,
                        # HNSW 파라미터
                        "INITIAL_CAP": 10000,
                        "M": 16,  # 각 노드의 최대 연결 수
                        "EF_CONSTRUCTION": 200  # 인덱스 구축 시 탐색 범위
                    }
                ),
                # 메타데이터 필드들
                TextField("question", sortable=True),
                TextField("source_url"),
                TextField("text"),
                NumericField("timestamp", sortable=True),
                TextField("custom_key"),
                TextField("id")
            )
            
            # 인덱스 정의
            definition = IndexDefinition(
                prefix=[f"doc:{self.index_name}:"],
                index_type=IndexType.HASH
            )
            
            # 인덱스 생성
            self.redis_client.ft(self.index_name).create_index(
                fields=schema,
                definition=definition
            )
            
            print(f"인덱스 '{self.index_name}' 생성 완료")
            
        except Exception as e:
            print(f"인덱스 생성 오류: {e}")
            raise
            
    def add_document(self, 
                     doc_id: str,
                     embedding: List[float],
                     metadata: Dict[str, Any]) -> bool:
        """
        문서와 임베딩 벡터를 인덱스에 추가
        
        Args:
            doc_id: 문서 고유 ID
            embedding: 임베딩 벡터
            metadata: 문서 메타데이터
            
        Returns:
            bool: 성공 여부
        """
        try:
            # 벡터를 바이트 배열로 변환
            embedding_bytes = np.array(embedding, dtype=np.float32).tobytes()
            
            # Redis에 저장할 데이터 준비
            doc_data = metadata.copy()
            doc_data["embedding_vector"] = embedding_bytes
            doc_data["custom_key"] = doc_id
            doc_data["id"] = doc_id
            
            # Redis Hash로 저장
            redis_key = f"doc:{self.index_name}:{doc_id}"
            self.redis_client.hset(redis_key, mapping=doc_data)
            
            return True
            
        except Exception as e:
            print(f"문서 추가 오류: {e}")
            return False
            
    def search_similar(self,
                      query_vector: List[float],
                      top_k: int = 5,
                      score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        유사한 벡터 검색 (HNSW 알고리즘 사용)
        
        Args:
            query_vector: 검색할 벡터
            top_k: 반환할 최대 결과 수
            score_threshold: 유사도 임계값
            
        Returns:
            List[Dict]: 검색 결과 리스트
        """
        # 검색 전 간단한 인덱스 상태 확인
        if not self.debugger.check_index_exists(self.index_name):
            print(f"❌ 검색 실패: 인덱스 '{self.index_name}' 없음")
            return []
        
        doc_count = self.debugger.count_documents_in_index(self.index_name)
        if doc_count == 0:
            print(f"⚠️ 인덱스 '{self.index_name}' 비어있음")
            return []
        
        try:
            # 쿼리 벡터를 바이트 배열로 변환
            query_bytes = np.array(query_vector, dtype=np.float32).tobytes()
            
            # 검색 쿼리 생성
            base_query = f"*=>[KNN {top_k} @embedding_vector $vector AS score]"
            query = Query(base_query)\
                .sort_by("score")\
                .paging(0, top_k)\
                .dialect(2)
            
            # 검색 로그 생략 가능
            
            # 검색 실행
            results = self.redis_client.ft(self.index_name).search(
                query,
                query_params={"vector": query_bytes}
            )
            
            # 결과 포맷팅
            formatted_results = []
            for doc in results.docs:
                # 코사인 유사도 점수 (1 - distance)
                similarity_score = 1 - float(doc.score)
                
                # 임계값 체크
                if similarity_score >= score_threshold:
                    # Redis에 저장된 원본 메타데이터를 그대로 가져오거나
                    # 필요한 모든 필드를 명시적으로 포함시켜야 합니다.
                    # 현재 코드는 doc.question, doc.source_url 등 일부만 가져오고 있을 수 있습니다.
                    
                    # 예시: 저장 시 사용한 모든 메타데이터 필드를 가져오도록 수정
                    # Redisearch 결과 객체 (doc)에서 모든 필드를 바로 딕셔너리로 변환하거나,
                    # add_document 시 저장한 필드 이름들을 정확히 명시해서 가져와야 합니다.
                    
                    # 현재 코드에서 메타데이터를 구성하는 방식 (수정 필요)
                    metadata_from_doc = {
                        "question": getattr(doc, 'question', None),
                        "source_url": getattr(doc, 'source_url', None),
                        "text": getattr(doc, 'text', None),
                        "timestamp": float(getattr(doc, 'timestamp', 0)) if hasattr(doc, 'timestamp') else None,
                        "id": getattr(doc, 'id', None),
                        "custom_key": getattr(doc, 'custom_key', None),
                        "answer": getattr(doc, 'answer', None),
                        "type": getattr(doc, 'type', None)
                    }

                    result_item = {
                        "key": getattr(doc, 'id', None),
                        "similarity": similarity_score,
                        "metadata": metadata_from_doc,
                        "redis_key": getattr(doc, 'id', None),
                        "question": getattr(doc, 'question', None),
                        "answer": getattr(doc, 'answer', None)
                    }
                    
                    formatted_results.append(result_item)
                    
            return formatted_results
            
        except Exception as e:
            print(f"벡터 검색 오류: {e}")
            import traceback
            traceback.print_exc()
            return []
            
    def update_ef_runtime(self, ef_runtime: int = 10):
        """
        런타임 검색 성능 파라미터 조정
        
        Args:
            ef_runtime: 검색 시 탐색할 이웃 수 (높을수록 정확하지만 느림)
        """
        try:
            # HNSW 런타임 파라미터 업데이트
            self.redis_client.ft(self.index_name).config_set(
                "HNSW_EF_RUNTIME", ef_runtime
            )
            print(f"EF_RUNTIME을 {ef_runtime}으로 설정했습니다.")
        except Exception as e:
            print(f"EF_RUNTIME 설정 오류: {e}")
            
    def get_index_info(self) -> Dict[str, Any]:
        """인덱스 정보 조회"""
        try:
            info = self.redis_client.ft(self.index_name).info()
            return info
        except Exception as e:
            print(f"인덱스 정보 조회 오류: {e}")
            return {}
            
    def delete_document(self, doc_id: str) -> bool:
        """문서 삭제"""
        try:
            redis_key = f"doc:{self.index_name}:{doc_id}"
            result = self.redis_client.delete(redis_key)
            return result > 0
        except Exception as e:
            print(f"문서 삭제 오류: {e}")
            return False

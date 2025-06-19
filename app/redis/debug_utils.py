# debug_utils.py
"""
Redis 인덱스 상태 확인을 위한 디버깅 유틸리티
"""

import redis
from typing import List, Dict, Any


class RedisIndexDebugger:
    """Redis 인덱스 상태를 확인하기 위한 디버깅 클래스"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def check_redis_connection(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            self.redis_client.ping()
            print("✅ Redis 연결 정상")
            return True
        except Exception as e:
            print(f"❌ Redis 연결 오류: {e}")
            return False
    
    def list_all_indices(self) -> List[str]:
        """모든 Redis 인덱스 목록 조회 (출력 간소화)"""
        try:
            indices = self.redis_client.execute_command("FT._LIST")
            index_list = [idx.decode('utf-8') if isinstance(idx, bytes) else str(idx) for idx in indices]
            print(f"📋 인덱스 목록: {index_list}")
            return index_list
        except Exception as e:
            print(f"❌ 인덱스 목록 조회 오류: {e}")
            return []
    
    def check_index_exists(self, index_name: str) -> bool:
        """특정 인덱스 존재 여부 확인"""
        try:
            info = self.redis_client.ft(index_name).info()
            print(f"✅ 인덱스 '{index_name}' 존재함")
            return True
        except redis.exceptions.ResponseError as e:
            if "No such index" in str(e):
                print(f"❌ 인덱스 '{index_name}' 존재하지 않음")
            else:
                print(f"❌ 인덱스 '{index_name}' 확인 오류: {e}")
            return False
        except Exception as e:
            print(f"❌ 인덱스 '{index_name}' 확인 중 예외 발생: {e}")
            return False
    
    def get_index_info(self, index_name: str) -> Dict[str, Any]:
        """인덱스 상세 정보 조회"""
        try:
            info = self.redis_client.ft(index_name).info()
            
            # 중요한 정보만 간단히 출력
            if isinstance(info, dict):
                doc_count = info.get('num_docs', 0)
                print(f"📊 인덱스 '{index_name}': {doc_count}개 문서")
            else:
                # info가 리스트인 경우 파싱
                doc_count = 0
                for i, item in enumerate(info):
                    if item == 'num_docs' and i + 1 < len(info):
                        doc_count = info[i + 1]
                        break
                print(f"📊 인덱스 '{index_name}': {doc_count}개 문서")
            
            return info
        except Exception as e:
            print(f"❌ 인덱스 '{index_name}' 정보 조회 오류: {e}")
            return {}
    
    def count_documents_in_index(self, index_name: str) -> int:
        """인덱스 내 문서 개수 확인 (출력 없이)"""
        try:
            info = self.redis_client.ft(index_name).info()
            if isinstance(info, dict):
                doc_count = info.get('num_docs', 0)
            else:
                # info가 리스트인 경우 파싱
                doc_count = 0
                for i, item in enumerate(info):
                    if item == 'num_docs' and i + 1 < len(info):
                        doc_count = info[i + 1]
                        break
            
            return int(doc_count)
        except Exception as e:
            return 0
    
    def check_redis_keys_by_pattern(self, pattern: str) -> List[str]:
        """패턴으로 Redis 키 확인 (출력 없이)"""
        try:
            keys = self.redis_client.keys(pattern)
            key_list = [key.decode('utf-8') if isinstance(key, bytes) else str(key) for key in keys]
            return key_list
        except Exception as e:
            return []
    
    def full_diagnosis(self, index_names: List[str] = None) -> Dict[str, Any]:
        """전체 진단 실행 (간단 버전)"""
        diagnosis = {
            "redis_connected": False,
            "all_indices": [],
            "target_indices_status": {},
            "key_patterns": {}
        }
        
        # 1. Redis 연결 확인
        diagnosis["redis_connected"] = self.check_redis_connection()
        if not diagnosis["redis_connected"]:
            return diagnosis
        
        # 2. 모든 인덱스 목록 조회
        diagnosis["all_indices"] = self.list_all_indices()
        
        # 3. 특정 인덱스들 상태 확인
        if index_names is None:
            index_names = ["document_index", "semantic_cache_index"]
        
        for index_name in index_names:
            index_status = {
                "exists": False,
                "info": {},
                "doc_count": 0,
                "related_keys_count": 0
            }
            
            # 인덱스 존재 확인
            index_status["exists"] = self.check_index_exists(index_name)
            
            if index_status["exists"]:
                # 인덱스 정보 조회 (간단히)
                index_status["info"] = self.get_index_info(index_name)
                # 문서 개수 확인
                index_status["doc_count"] = self.count_documents_in_index(index_name)
            
            # 관련 키 패턴 확인
            key_pattern = f"doc:{index_name}:*"
            related_keys = self.check_redis_keys_by_pattern(key_pattern)
            index_status["related_keys_count"] = len(related_keys)
            
            diagnosis["target_indices_status"][index_name] = index_status
        
        # 간단한 요약 출력
        print(f"🔍 진단 완료: {len([i for i in diagnosis['all_indices'] if i])}개 인덱스 존재")
        
        return diagnosis

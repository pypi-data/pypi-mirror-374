"""
인과관계 감지 시스템 (v2.4.0.dev1)

브릿지 메모리 개념과 벡터 기반 최적화를 통한 인과관계 연결 시스템
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import re
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
import threading

logger = logging.getLogger(__name__)

@dataclass
class CausalityScore:
    """인과관계 강도 점수"""
    strength: float  # 0.0 ~ 1.0
    confidence: float  # 신뢰도
    breakdown: Dict[str, float]  # 세부 점수 분석
    direction: str  # 'forward' or 'backward' 또는 'bidirectional'

@dataclass 
class BridgeConnection:
    """브릿지 메모리 연결 정보"""
    start_memory_id: int
    bridge_memory_id: int  
    end_memory_id: int
    bridge_score: float
    chain_type: str  # 'problem_solving', 'learning', 'decision_making' 등
    
@dataclass
class CausalChain:
    """완전한 인과관계 체인"""
    memories: List[Dict[str, Any]]
    causality_scores: List[float]
    chain_confidence: float
    story_summary: str

class VectorBasedCausalityFilter:
    """128차원 벡터를 활용한 인과관계 후보 축소"""
    
    def __init__(self, similarity_threshold_min=0.1, similarity_threshold_max=0.95):
        self.similarity_threshold_min = similarity_threshold_min
        self.similarity_threshold_max = similarity_threshold_max
        
    def find_causality_candidates(self, new_memory: Dict[str, Any], 
                                 existing_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """적응형 벡터 유사도 후보 축소 - 메모리 개수에 따른 동적 조정"""
        
        if 'embedding' not in new_memory or not new_memory['embedding']:
            logger.warning("새 메모리에 임베딩 벡터가 없음")
            return self._adaptive_fallback(existing_memories)
            
        new_vector = np.array(new_memory['embedding'])
        candidates = []
        total_memories = len(existing_memories)
        
        # 적응형 후보 수 결정
        max_candidates = self._get_adaptive_candidate_count(total_memories)
        
        # 적응형 유사도 임계값 조정
        similarity_thresholds = self._get_adaptive_thresholds(total_memories)
        
        for memory in existing_memories:
            if 'embedding' not in memory or not memory['embedding']:
                continue
                
            existing_vector = np.array(memory['embedding'])
            
            # 코사인 유사도 계산
            similarity = self._cosine_similarity(new_vector, existing_vector)
            
            # 적응형 Sweet Spot 범위 적용
            if similarity_thresholds['min'] <= similarity <= similarity_thresholds['max']:
                candidates.append((memory, similarity))
                
        # 유사도 순 정렬 후 적응형 개수만큼 반환
        candidates.sort(key=lambda x: x[1], reverse=True)
        result = [mem for mem, sim in candidates[:max_candidates]]
        
        logger.debug(f"적응형 벡터 필터링: {total_memories}개 → {len(result)}개 (최대 {max_candidates}개)")
        return result
    
    def _get_adaptive_candidate_count(self, total_memories: int) -> int:
        """메모리 개수에 따른 적응형 후보 수 결정"""
        if total_memories < 50:
            return min(20, total_memories // 2)  # 소규모: 더 많은 후보 (최대 20개)
        elif total_memories < 200:
            return min(15, total_memories // 10)  # 중간: 적당한 후보 (최대 15개) 
        elif total_memories < 500:
            return min(12, total_memories // 25)  # 중대규모: 제한적 후보 (최대 12개)
        else:
            return min(10, total_memories // 50)  # 대규모: 엄격한 필터링 (최대 10개)
    
    def _get_adaptive_thresholds(self, total_memories: int) -> Dict[str, float]:
        """메모리 개수에 따른 적응형 유사도 임계값"""
        if total_memories < 50:
            return {'min': 0.05, 'max': 0.97}  # 소규모: 넓은 범위
        elif total_memories < 200:
            return {'min': 0.08, 'max': 0.95}  # 중간: 표준 범위
        elif total_memories < 500:
            return {'min': 0.12, 'max': 0.92}  # 중대규모: 좁은 범위
        else:
            return {'min': 0.15, 'max': 0.90}  # 대규모: 매우 엄격한 범위
    
    def _adaptive_fallback(self, existing_memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """임베딩이 없을 때의 적응형 폴백"""
        total = len(existing_memories)
        if total < 50:
            return existing_memories[-30:]  # 소규모: 최근 30개
        elif total < 200:
            return existing_memories[-20:]  # 중간: 최근 20개
        else:
            return existing_memories[-15:]  # 대규모: 최근 15개만
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """코사인 유사도 계산"""
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
            
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(vec1, vec2) / (norm1 * norm2))


class BasicCausalityDetector:
    """기본 인과관계 패턴 매칭 시스템 + 스마트 캐싱"""
    
    def __init__(self):
        # 스마트 캐싱 시스템
        self.causality_cache = {}  # {(mem_a_id, mem_b_id): CausalityScore}
        self.cache_stats = {'hits': 0, 'misses': 0, 'size': 0}
        self.max_cache_size = 10000  # 최대 캐시 크기
        
        # LRU 캐시를 위한 접근 순서 추적
        from collections import OrderedDict
        self.cache_access_order = OrderedDict()
        
        # 한국어/영어 인과관계 키워드 패턴
        self.causal_patterns = {
            'strong_cause': [
                # 한국어 강한 인과관계 패턴
                r'(.+)(때문에|덕분에|으로 인해|의 결과로)(.+)',
                r'(.+)(해서|니까|라서|여서)(.+)', 
                # 영어 강한 인과관계 패턴
                r'(.+)(because|due to|as a result|consequently)(.+)',
                r'(.+)(so|therefore|thus|hence)(.+)'
            ],
            'medium_cause': [
                # 중간 강도 패턴
                r'(.+)(그래서|그러니까|따라서|이에)(.+)',
                r'(.+)(then|next|after that|subsequently)(.+)',
                r'(.+)(해결|개선|수정|fix|solve|resolve)(.+)'
            ],
            'weak_cause': [
                # 약한 인과관계 패턴
                r'(.+)(이후|다음|후에|later|after)(.+)',
                r'(.+)(관련|연관|관해서|about|regarding)(.+)'
            ],
            'problem_solution': [
                r'(.+)(문제|이슈|버그|오류).*(해결|수정|개선)',
                r'(.+)(problem|issue|error).*(fix|solve|resolve)',
            ]
        }
        
        # 패턴별 가중치
        self.pattern_weights = {
            'strong_cause': 1.0,
            'medium_cause': 0.7, 
            'weak_cause': 0.4,
            'problem_solution': 0.9
        }
        
    def detect_causality(self, memory_a: Dict[str, Any], 
                        memory_b: Dict[str, Any]) -> CausalityScore:
        """스마트 캐싱이 적용된 인과관계 감지 및 점수 계산"""
        
        # 캐싱 시스템 (임시로 조건부 활성화)
        use_cache = hasattr(self, 'causality_cache') and hasattr(self, '_get_cache_key')
        
        if use_cache:
            # 캐시 키 생성
            cache_key = self._get_cache_key(memory_a, memory_b)
            
            # 캐시 히트 확인
            if cache_key in self.causality_cache:
                self.cache_stats['hits'] += 1
                # LRU 캐시: 접근된 항목을 맨 뒤로 이동
                self.cache_access_order.move_to_end(cache_key)
                return self.causality_cache[cache_key]
            
            # 캐시 미스: 새로 계산
            self.cache_stats['misses'] += 1
        
        # 1. 시간적 관계 점수
        temporal_score = self._calculate_temporal_score(memory_a, memory_b)
        
        # 2. 언어적 패턴 점수
        linguistic_score = self._calculate_linguistic_score(memory_a, memory_b)
        
        # 3. 벡터 유사도 점수 (의미적 관련성)
        semantic_score = self._calculate_semantic_score(memory_a, memory_b)
        
        # 4. 종합 점수 계산 (가중 평균)
        final_score = (
            temporal_score * 0.25 +
            linguistic_score * 0.35 +  # 언어적 신호가 가장 중요
            semantic_score * 0.40
        )
        
        # 5. 방향성 결정
        direction = self._determine_direction(memory_a, memory_b, temporal_score, linguistic_score)
        
        # 6. 신뢰도 계산
        confidence = self._calculate_confidence(temporal_score, linguistic_score, semantic_score)
        
        # 결과 생성
        result = CausalityScore(
            strength=final_score,
            confidence=confidence,
            breakdown={
                'temporal': temporal_score,
                'linguistic': linguistic_score,
                'semantic': semantic_score
            },
            direction=direction
        )
        
        # 캐시에 저장 (LRU 적용)
        if use_cache:
            self._cache_result(cache_key, result)
        
        return result
    
    def _calculate_temporal_score(self, memory_a: Dict[str, Any], 
                                 memory_b: Dict[str, Any]) -> float:
        """시간적 관계 점수 계산"""
        try:
            time_a = datetime.fromisoformat(memory_a['timestamp'])
            time_b = datetime.fromisoformat(memory_b['timestamp'])
            
            time_diff = abs((time_b - time_a).total_seconds())
            
            # 시간 차이에 따른 점수 (가까울수록 높은 점수)
            if time_diff < 3600:  # 1시간 이내
                return 1.0
            elif time_diff < 86400:  # 1일 이내  
                return 0.8
            elif time_diff < 604800:  # 1주 이내
                return 0.6
            elif time_diff < 2592000:  # 1개월 이내
                return 0.4
            else:
                return 0.2
                
        except (ValueError, KeyError):
            return 0.3  # 시간 정보 없으면 중간 점수
    
    def _calculate_linguistic_score(self, memory_a: Dict[str, Any], 
                                   memory_b: Dict[str, Any]) -> float:
        """언어적 패턴 점수 계산"""
        
        text_combined = f"{memory_a.get('context', '')} {memory_b.get('context', '')}"
        max_score = 0.0
        
        for pattern_type, patterns in self.causal_patterns.items():
            weight = self.pattern_weights[pattern_type]
            
            for pattern in patterns:
                if re.search(pattern, text_combined, re.IGNORECASE):
                    score = weight
                    max_score = max(max_score, score)
                    break  # 패턴 타입별로 하나만 매칭
                    
        return max_score
    
    def _calculate_semantic_score(self, memory_a: Dict[str, Any], 
                                 memory_b: Dict[str, Any]) -> float:
        """의미적 유사도 점수 계산"""
        
        if 'embedding' not in memory_a or 'embedding' not in memory_b:
            return 0.5  # 임베딩 없으면 중간 점수
            
        try:
            vec_a = np.array(memory_a['embedding'])
            vec_b = np.array(memory_b['embedding'])
            
            # 코사인 유사도 계산
            similarity = VectorBasedCausalityFilter()._cosine_similarity(vec_a, vec_b)
            
            # 0~1 범위로 정규화 (코사인 유사도는 -1~1)
            return (similarity + 1) / 2
            
        except (ValueError, TypeError):
            return 0.5
    
    def _determine_direction(self, memory_a: Dict[str, Any], memory_b: Dict[str, Any], 
                           temporal_score: float, linguistic_score: float) -> str:
        """인과관계 방향성 결정"""
        
        try:
            time_a = datetime.fromisoformat(memory_a['timestamp'])
            time_b = datetime.fromisoformat(memory_b['timestamp'])
            
            # 시간 순서 기반 방향성
            if time_a < time_b:
                return 'forward'  # A → B
            elif time_a > time_b:
                return 'backward'  # B → A  
            else:
                return 'bidirectional'  # 동시간대
                
        except (ValueError, KeyError):
            return 'unknown'
    
    def _calculate_confidence(self, temporal: float, linguistic: float, semantic: float) -> float:
        """종합 신뢰도 계산"""
        
        # 세 점수가 모두 높을 때 높은 신뢰도
        min_score = min(temporal, linguistic, semantic)
        avg_score = (temporal + linguistic + semantic) / 3
        
        # 최소값과 평균값의 조화평균 (모든 지표가 균형있게 높아야 함)
        if min_score + avg_score == 0:
            return 0.0
            
        confidence = 2 * min_score * avg_score / (min_score + avg_score)
        return min(confidence, 1.0)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': self.cache_stats['size'],
            'max_cache_size': self.max_cache_size,
            'total_hits': self.cache_stats['hits'],
            'total_misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }


class BridgeMemoryDetector:
    """브릿지 메모리 감지 시스템 - 핵심 혁신 기능"""
    
    def __init__(self, bridge_threshold=0.5):
        self.causality_detector = BasicCausalityDetector()
        self.vector_filter = VectorBasedCausalityFilter()
        self.bridge_threshold = bridge_threshold  # 설정 가능한 임계값
        
    def detect_bridge_opportunities(self, new_memory: Dict[str, Any], 
                                   existing_memories: List[Dict[str, Any]]) -> List[BridgeConnection]:
        """새 메모리가 기존 메모리들을 연결하는 브릿지 역할 감지"""
        
        bridge_connections = []
        
        # 1단계: 벡터 기반으로 관련성 높은 메모리들 선별
        relevant_memories = self.vector_filter.find_causality_candidates(new_memory, existing_memories)
        
        if len(relevant_memories) < 2:
            return []  # 브릿지 역할 불가능
            
        # 2단계: 관련 메모리들 중에서 브릿지 기회 탐색
        for i, mem_a in enumerate(relevant_memories):
            for j, mem_c in enumerate(relevant_memories[i+1:], i+1):
                
                # A와 C 사이에 직접적 연결이 없는 경우만 (향후 구현)
                # if self._has_direct_connection(mem_a, mem_c):
                #     continue
                
                # 새 메모리가 A → new_memory → C 체인을 만들 수 있는지 검사
                bridge_score = self._calculate_bridge_score(mem_a, new_memory, mem_c)
                
                if bridge_score.strength > 0.4:  # 브릿지 임계값 낮춤 (dev1 테스트용)
                    bridge_connections.append(
                        BridgeConnection(
                            start_memory_id=mem_a.get('block_index', 0),
                            bridge_memory_id=new_memory.get('block_index', 0),
                            end_memory_id=mem_c.get('block_index', 0), 
                            bridge_score=bridge_score.strength,
                            chain_type=self._identify_chain_type(mem_a, new_memory, mem_c)
                        )
                    )
                    
        logger.info(f"브릿지 연결 발견: {len(bridge_connections)}개")
        return bridge_connections
    
    def _calculate_bridge_score(self, mem_a: Dict[str, Any], bridge: Dict[str, Any], 
                               mem_c: Dict[str, Any]) -> CausalityScore:
        """A → Bridge → C 체인의 타당성 점수"""
        
        # A → Bridge 인과관계 점수
        causality_ab = self.causality_detector.detect_causality(mem_a, bridge)
        
        # Bridge → C 인과관계 점수  
        causality_bc = self.causality_detector.detect_causality(bridge, mem_c)
        
        # 시간적 순서 검증 (A < Bridge < C)
        temporal_order_score = self._validate_temporal_order(mem_a, bridge, mem_c)
        
        # 브릿지 점수 = 두 연결의 조화평균 * 시간 순서 가중치
        if causality_ab.strength + causality_bc.strength == 0:
            bridge_strength = 0.0
        else:
            bridge_strength = (2 * causality_ab.strength * causality_bc.strength) / \
                            (causality_ab.strength + causality_bc.strength)
            bridge_strength *= temporal_order_score  # 시간 순서 가중치 적용
            
        # 종합 신뢰도
        bridge_confidence = min(causality_ab.confidence, causality_bc.confidence) * temporal_order_score
        
        return CausalityScore(
            strength=bridge_strength,
            confidence=bridge_confidence,
            breakdown={
                'causality_ab': causality_ab.strength,
                'causality_bc': causality_bc.strength,
                'temporal_order': temporal_order_score
            },
            direction='bridge'
        )
    
    def _validate_temporal_order(self, mem_a: Dict[str, Any], bridge: Dict[str, Any], 
                                mem_c: Dict[str, Any]) -> float:
        """시간적 순서 검증 (A ≤ Bridge ≤ C)"""
        
        try:
            time_a = datetime.fromisoformat(mem_a['timestamp'])
            time_bridge = datetime.fromisoformat(bridge['timestamp'])
            time_c = datetime.fromisoformat(mem_c['timestamp'])
            
            # 완벽한 순서: A ≤ Bridge ≤ C
            if time_a <= time_bridge <= time_c:
                return 1.0
            
            # 부분적 순서 (일부만 맞음)
            if time_a <= time_bridge or time_bridge <= time_c:
                return 0.7
                
            # 순서가 맞지 않지만 시간 차이가 작음 (동시간대)
            max_diff = max(
                abs((time_bridge - time_a).total_seconds()),
                abs((time_c - time_bridge).total_seconds())
            )
            
            if max_diff < 86400:  # 1일 이내
                return 0.5
            else:
                return 0.2
                
        except (ValueError, KeyError):
            return 0.3  # 시간 정보 없으면 중간 점수
    
    def _identify_chain_type(self, mem_a: Dict[str, Any], bridge: Dict[str, Any], 
                           mem_c: Dict[str, Any]) -> str:
        """인과관계 체인 타입 식별"""
        
        contexts = [
            mem_a.get('context', '').lower(),
            bridge.get('context', '').lower(), 
            mem_c.get('context', '').lower()
        ]
        
        combined_text = ' '.join(contexts)
        
        # 문제해결 패턴
        if any(word in combined_text for word in ['문제', '이슈', '버그', '해결', 'problem', 'issue', 'fix', 'solve']):
            return 'problem_solving'
        
        # 학습 패턴    
        if any(word in combined_text for word in ['공부', '학습', '배웠', 'learn', 'study', 'understand']):
            return 'learning'
        
        # 의사결정 패턴
        if any(word in combined_text for word in ['결정', '선택', '결론', 'decide', 'choose', 'decision']):
            return 'decision_making'
        
        # 개발 패턴
        if any(word in combined_text for word in ['개발', '구현', '코딩', 'develop', 'implement', 'code']):
            return 'development'
            
        return 'general'
    
    def detect_bridge_connection(self, new_memory: Dict[str, Any], bridge_candidate: Dict[str, Any], 
                               target_memory: Dict[str, Any] = None) -> Optional[CausalityScore]:
        """브릿지 연결 감지 (API 호환성을 위한 메서드)"""
        if target_memory is None:
            # 타겟이 없으면 브릿지 스코어만 계산
            return CausalityScore(
                strength=0.5,
                confidence=0.5,
                breakdown={'bridge_type': 'single'},
                direction='bridge'
            )
        
        # 실제 브릿지 스코어 계산
        return self._calculate_bridge_score(target_memory, new_memory, bridge_candidate)
    
    def _get_cache_key(self, memory_a: Dict[str, Any], memory_b: Dict[str, Any]) -> Tuple[int, int]:
        """캐시 키 생성 - 메모리 ID 기반"""
        id_a = memory_a.get('block_index', hash(memory_a.get('context', '')))
        id_b = memory_b.get('block_index', hash(memory_b.get('context', '')))
        # 순서에 상관없이 동일한 키 생성 (양방향 캐시)
        return tuple(sorted([id_a, id_b]))
    
    def _cache_result(self, cache_key: Tuple[int, int], result: CausalityScore):
        """결과를 캐시에 저장 (LRU 적용)"""
        
        # 캐시 크기 제한 확인
        if len(self.causality_cache) >= self.max_cache_size:
            # LRU: 가장 오래된 항목 제거
            oldest_key = next(iter(self.cache_access_order))
            del self.causality_cache[oldest_key]
            del self.cache_access_order[oldest_key]
        
        # 새 결과 저장
        self.causality_cache[cache_key] = result
        self.cache_access_order[cache_key] = True
        self.cache_stats['size'] = len(self.causality_cache)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = self.cache_stats['hits'] / total_requests if total_requests > 0 else 0
        
        return {
            'cache_size': self.cache_stats['size'],
            'max_cache_size': self.max_cache_size,
            'total_hits': self.cache_stats['hits'],
            'total_misses': self.cache_stats['misses'],
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def clear_cache(self):
        """캐시 초기화"""
        self.causality_cache.clear()
        self.cache_access_order.clear()
        self.cache_stats = {'hits': 0, 'misses': 0, 'size': 0}


class CausalitySystem:
    """통합 인과관계 시스템 - 계층적 처리 + 메인 엔트리 포인트"""
    
    def __init__(self, bridge_threshold=0.5):
        self.vector_filter = VectorBasedCausalityFilter()
        self.causality_detector = BasicCausalityDetector()
        self.bridge_detector = BridgeMemoryDetector(bridge_threshold)
        
        # 계층적 분석 임계값 설정
        self.tier_thresholds = {
            'tier1_strong': 0.7,    # 강한 연결 (필수 분석)
            'tier2_medium': 0.4,    # 중간 연결 (선택적 분석)
            'tier3_weak': 0.2       # 약한 연결 (명시적 요청시만)
        }
        
        # 중요도 기반 시간 윈도우 설정
        self.time_window_config = {
            'enabled': True,        # 시간 윈도우 온오프
            'critical_hours': 24,   # 중요 정보: 24시간 윈도우
            'important_days': 7,    # 중요 정보: 7일 윈도우  
            'normal_days': 30,      # 일반 정보: 30일 윈도우
            'low_days': 90          # 낮은 중요도: 90일 윈도우
        }
        
        # 병렬 처리 설정
        self.parallel_config = {
            'enabled': True,
            'max_workers': min(multiprocessing.cpu_count(), 8),  # CPU 코어 수와 8 중 작은 값
            'chunk_threshold': 20  # 20개 이상 후보시 병렬 처리 활성화
        }
        
    def process_new_memory(self, new_memory: Dict[str, Any], 
                          existing_memories: List[Dict[str, Any]], 
                          analysis_depth: str = 'balanced',
                          time_window_enabled: bool = None,
                          memory_importance: str = 'normal') -> Dict[str, Any]:
        """계층적 분석과 중요도 기반 시간 윈도우를 통한 새 메모리 인과관계 분석"""
        
        logger.info(f"새 메모리 인과관계 분석 시작: {new_memory.get('block_index', 'N/A')} (깊이: {analysis_depth}, 중요도: {memory_importance})")
        
        # 시간 윈도우 필터링 적용 (온오프 가능)
        if time_window_enabled is None:
            time_window_enabled = self.time_window_config['enabled']
        
        if time_window_enabled:
            existing_memories = self._apply_time_window_filter(new_memory, existing_memories, memory_importance)
            logger.debug(f"시간 윈도우 필터링 적용: {len(existing_memories)}개 메모리로 축소")
        
        # 분석 깊이에 따른 계층적 처리
        if analysis_depth == 'quick':
            return self._quick_analysis(new_memory, existing_memories)
        elif analysis_depth == 'balanced':
            return self._balanced_analysis(new_memory, existing_memories)
        elif analysis_depth == 'deep':
            return self._deep_analysis(new_memory, existing_memories)
        else:
            return self._balanced_analysis(new_memory, existing_memories)
    
    def _apply_time_window_filter(self, new_memory: Dict[str, Any], 
                                 existing_memories: List[Dict[str, Any]], 
                                 importance: str = 'normal') -> List[Dict[str, Any]]:
        """중요도 기반 시간 윈도우 필터링"""
        
        try:
            new_timestamp = datetime.fromisoformat(new_memory['timestamp'])
        except (ValueError, KeyError):
            logger.warning("새 메모리의 타임스탬프가 없음 - 시간 윈도우 필터링 건너뜀")
            return existing_memories
        
        # 중요도에 따른 윈도우 크기 결정
        if importance == 'critical':
            window_hours = self.time_window_config['critical_hours']
            window_delta = timedelta(hours=window_hours)
        elif importance == 'important':
            window_days = self.time_window_config['important_days']
            window_delta = timedelta(days=window_days)
        elif importance == 'normal':
            window_days = self.time_window_config['normal_days']
            window_delta = timedelta(days=window_days)
        elif importance == 'low':
            window_days = self.time_window_config['low_days']
            window_delta = timedelta(days=window_days)
        else:
            logger.warning(f"알 수 없는 중요도 '{importance}' - 기본 30일 윈도우 사용")
            window_delta = timedelta(days=30)
        
        # 시간 윈도우 범위 계산
        window_start = new_timestamp - window_delta
        window_end = new_timestamp + window_delta  # 양방향 윈도우
        
        # 필터링 적용
        filtered_memories = []
        for memory in existing_memories:
            try:
                memory_timestamp = datetime.fromisoformat(memory['timestamp'])
                if window_start <= memory_timestamp <= window_end:
                    filtered_memories.append(memory)
            except (ValueError, KeyError):
                # 타임스탬프가 없는 메모리는 포함 (안전 장치)
                filtered_memories.append(memory)
        
        logger.debug(f"시간 윈도우 필터링 결과: {len(existing_memories)}개 → {len(filtered_memories)}개 (중요도: {importance}, 윈도우: {window_delta})")
        return filtered_memories
    
    def configure_time_window(self, enabled: bool = True, 
                             critical_hours: int = 24,
                             important_days: int = 7,
                             normal_days: int = 30,
                             low_days: int = 90):
        """시간 윈도우 설정 변경"""
        
        self.time_window_config.update({
            'enabled': enabled,
            'critical_hours': critical_hours,
            'important_days': important_days,
            'normal_days': normal_days,
            'low_days': low_days
        })
        
        logger.info(f"시간 윈도우 설정 변경: enabled={enabled}, critical={critical_hours}h, important={important_days}d, normal={normal_days}d, low={low_days}d")
    
    def _process_candidates_parallel(self, new_memory: Dict[str, Any], 
                                   candidates: List[Dict[str, Any]], 
                                   min_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """후보 메모리들을 병렬로 처리하여 인과관계 감지"""
        
        if not self.parallel_config['enabled'] or len(candidates) < self.parallel_config['chunk_threshold']:
            # 병렬 처리 비활성화 또는 후보가 적을 때는 순차 처리
            return self._process_candidates_sequential(new_memory, candidates, min_threshold)
        
        logger.debug(f"병렬 처리 시작: {len(candidates)}개 후보, {self.parallel_config['max_workers']}개 워커")
        
        # 후보를 청크로 분할
        chunk_size = max(1, len(candidates) // self.parallel_config['max_workers'])
        chunks = [candidates[i:i + chunk_size] for i in range(0, len(candidates), chunk_size)]
        
        results = []
        with ThreadPoolExecutor(max_workers=self.parallel_config['max_workers']) as executor:
            # 각 청크를 병렬로 처리
            future_to_chunk = {
                executor.submit(self._process_chunk, new_memory, chunk, min_threshold): chunk 
                for chunk in chunks
            }
            
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as exc:
                    logger.error(f"청크 처리 중 오류: {exc}")
        
        logger.debug(f"병렬 처리 완료: {len(results)}개 결과 생성")
        return results
    
    def _process_candidates_sequential(self, new_memory: Dict[str, Any], 
                                     candidates: List[Dict[str, Any]], 
                                     min_threshold: float = 0.2) -> List[Dict[str, Any]]:
        """후보 메모리들을 순차적으로 처리 (폴백 방식)"""
        
        results = []
        for candidate in candidates:
            causality_score = self.causality_detector.detect_causality(new_memory, candidate)
            
            if causality_score.strength >= min_threshold:
                results.append({
                    'memory_id': candidate.get('block_index', 0),
                    'causality_score': causality_score.strength,
                    'confidence': causality_score.confidence,
                    'direction': causality_score.direction
                })
        
        return results
    
    def _process_chunk(self, new_memory: Dict[str, Any], 
                      chunk: List[Dict[str, Any]], 
                      min_threshold: float) -> List[Dict[str, Any]]:
        """청크를 처리하는 워커 함수 (스레드 안전)"""
        
        # 각 스레드에서 별도의 causality_detector 인스턴스 사용 (스레드 안전성)
        local_detector = BasicCausalityDetector()
        results = []
        
        for candidate in chunk:
            try:
                causality_score = local_detector.detect_causality(new_memory, candidate)
                
                if causality_score.strength >= min_threshold:
                    results.append({
                        'memory_id': candidate.get('block_index', 0),
                        'causality_score': causality_score.strength,
                        'confidence': causality_score.confidence,
                        'direction': causality_score.direction
                    })
            except Exception as e:
                logger.error(f"후보 처리 중 오류: {e}")
                continue
        
        return results
    
    def configure_parallel_processing(self, enabled: bool = True, 
                                    max_workers: int = None,
                                    chunk_threshold: int = 20):
        """병렬 처리 설정 변경"""
        
        if max_workers is None:
            max_workers = min(multiprocessing.cpu_count(), 8)
        
        self.parallel_config.update({
            'enabled': enabled,
            'max_workers': max_workers,
            'chunk_threshold': chunk_threshold
        })
        
        logger.info(f"병렬 처리 설정 변경: enabled={enabled}, max_workers={max_workers}, chunk_threshold={chunk_threshold}")
    
    def _quick_analysis(self, new_memory: Dict[str, Any], 
                       existing_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """빠른 분석 - Tier 1 (강한 연결)만 검사"""
        
        logger.debug("빠른 분석 모드: Tier 1 강한 연결만 검사")
        
        # 1단계: 벡터 기반 후보 축소 (더 엄격한 필터링)
        candidates = self.vector_filter.find_causality_candidates(new_memory, existing_memories)
        candidates = candidates[:10]  # 상위 10개만
        
        # 2단계: 강한 인과관계만 감지 (병렬 처리 적용)
        direct_causality = self._process_candidates_parallel(
            new_memory, candidates, self.tier_thresholds['tier1_strong'])
        
        # tier 정보 추가
        for link in direct_causality:
            link['tier'] = 'tier1_strong'
        
        return {
            'analysis_type': 'quick',
            'direct_links': direct_causality,
            'bridge_connections': [],  # 빠른 분석에서는 브릿지 건너뛰기
            'total_candidates_checked': len(candidates),
            'cache_stats': self.causality_detector.get_cache_stats()
        }
    
    def _balanced_analysis(self, new_memory: Dict[str, Any], 
                          existing_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """균형 분석 - Tier 1~2 (강한~중간 연결) 검사"""
        
        logger.debug("균형 분석 모드: Tier 1-2 강한~중간 연결 검사")
        
        # 1단계: 벡터 기반 후보 축소 (표준 필터링)
        candidates = self.vector_filter.find_causality_candidates(new_memory, existing_memories)
        
        # 2단계: 직접적 인과관계 감지 (Tier 1~2)
        direct_causality = []
        for candidate in candidates:
            causality_score = self.causality_detector.detect_causality(new_memory, candidate)
            
            if causality_score.strength >= self.tier_thresholds['tier2_medium']:
                tier = 'tier1_strong' if causality_score.strength >= self.tier_thresholds['tier1_strong'] else 'tier2_medium'
                direct_causality.append({
                    'memory_id': candidate.get('block_index', 0),
                    'causality_score': causality_score.strength,
                    'confidence': causality_score.confidence,
                    'direction': causality_score.direction,
                    'tier': tier
                })
        
        # 3단계: 브릿지 연결 감지 (제한적)
        bridge_connections = []
        if len(direct_causality) >= 2:  # 직접 연결이 2개 이상일 때만
            strong_candidates = [c for c in candidates 
                               if any(d['memory_id'] == c.get('block_index', 0) 
                                     for d in direct_causality)][:5]  # 상위 5개만
            
            for bridge_candidate in strong_candidates:
                bridge_score = self.bridge_detector.detect_bridge_connection(
                    new_memory, bridge_candidate, direct_causality[0] if direct_causality else None)
                
                if bridge_score and bridge_score.strength > 0.5:
                    bridge_connections.append({
                        'bridge_memory_id': bridge_candidate.get('block_index', 0),
                        'bridge_strength': bridge_score.strength,
                        'connection_type': bridge_score.breakdown.get('temporal_order', 'unknown')
                    })
        
        return {
            'analysis_type': 'balanced',
            'direct_links': direct_causality,
            'bridge_connections': bridge_connections,
            'total_candidates_checked': len(candidates),
            'cache_stats': self.causality_detector.get_cache_stats()
        }
    
    def _deep_analysis(self, new_memory: Dict[str, Any], 
                      existing_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """심화 분석 - 모든 Tier (약한 연결까지) 검사"""
        
        logger.debug("심화 분석 모드: 모든 Tier 약한 연결까지 검사")
        
        # 1단계: 벡터 기반 후보 축소 (완전 필터링)
        candidates = self.vector_filter.find_causality_candidates(new_memory, existing_memories)
        
        # 2단계: 모든 수준의 인과관계 감지 (Tier 1~3)
        direct_causality = []
        for candidate in candidates:
            causality_score = self.causality_detector.detect_causality(new_memory, candidate)
            
            if causality_score.strength >= self.tier_thresholds['tier3_weak']:
                if causality_score.strength >= self.tier_thresholds['tier1_strong']:
                    tier = 'tier1_strong'
                elif causality_score.strength >= self.tier_thresholds['tier2_medium']:
                    tier = 'tier2_medium'  
                else:
                    tier = 'tier3_weak'
                    
                direct_causality.append({
                    'memory_id': candidate.get('block_index', 0),
                    'causality_score': causality_score.strength,
                    'confidence': causality_score.confidence,
                    'direction': causality_score.direction,
                    'tier': tier
                })
        
        # 3단계: 완전한 브릿지 연결 감지
        bridge_connections = []
        if len(candidates) >= 3:  # 충분한 후보가 있을 때만
            for bridge_candidate in candidates[:10]:  # 상위 10개 후보만
                for target_memory in direct_causality[:5]:  # 상위 5개 직접 연결만
                    target_mem = next((c for c in candidates 
                                     if c.get('block_index', 0) == target_memory['memory_id']), None)
                    if target_mem:
                        bridge_score = self.bridge_detector.detect_bridge_connection(
                            new_memory, bridge_candidate, target_mem)
                        
                        if bridge_score and bridge_score.strength > 0.4:  # 낮은 임계값
                            bridge_connections.append({
                                'bridge_memory_id': bridge_candidate.get('block_index', 0),
                                'target_memory_id': target_memory['memory_id'], 
                                'bridge_strength': bridge_score.strength,
                                'connection_type': bridge_score.breakdown.get('temporal_order', 'unknown'),
                                'chain_type': getattr(bridge_score, 'direction', 'bridge')
                            })
        
        return {
            'analysis_type': 'deep',
            'direct_links': direct_causality,
            'bridge_connections': bridge_connections,
            'total_candidates_checked': len(candidates),
            'tier_breakdown': {
                'tier1_strong': len([d for d in direct_causality if d['tier'] == 'tier1_strong']),
                'tier2_medium': len([d for d in direct_causality if d['tier'] == 'tier2_medium']),
                'tier3_weak': len([d for d in direct_causality if d['tier'] == 'tier3_weak'])
            },
            'cache_stats': self.causality_detector.get_cache_stats()
        }


# 편의 함수들
def detect_causality_for_memory(new_memory: Dict[str, Any], 
                               existing_memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """새 메모리의 인과관계 분석 (메인 API)"""
    
    system = CausalitySystem()
    return system.process_new_memory(new_memory, existing_memories)


def get_causality_chains(memory_ids: List[int], memories: List[Dict[str, Any]]) -> List[CausalChain]:
    """메모리 ID 목록으로부터 인과관계 체인 구성"""
    
    # TODO: 추후 구현 예정 (체인 재구성 및 스토리 생성)
    pass
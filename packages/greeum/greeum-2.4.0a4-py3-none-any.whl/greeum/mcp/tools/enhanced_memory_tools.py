"""
v2.4.0a2 목표 1: MCP 도구 description을 통한 마이크로 기억 단위 사용 유도

핵심 아이디어: AI가 더 작은 기억 단위로 더 자주 메모리 도구를 사용하도록
description에서 구체적으로 유도하는 문구 작성
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

# 기존 도구 import (순환 import 방지를 위해 제거)
# from .enhanced_memory_tools import EnhancedMemoryTools


# MCP 서버 도구 함수들 - description 최적화 버전

async def add_memory_frequent(content: str, importance: float = 0.5) -> str:
    """
    Immediate Memory Storage with Greimas Actant Model: Record all interactions using [Subject-Action-Object] structure
    
    Core Principle: Every work unit has permanent preservation value - prioritize pattern accumulation over importance filtering.
    
    Store immediately at these interaction points:
    - User questions/requests -> [User-Request-SpecificFeature]
    - Claude responses/solutions -> [Claude-Provide-Solution] + detailed answer
    - Tool execution results -> [Claude-Execute-ToolName] + outcome + analysis
    - Problem discovery/resolution -> [Actor-Discover-Issue] + solution process  
    - Task transition points -> [Subject-Transition-NewTask] + context
    - Code changes/implementations -> [Claude-Implement-Feature] + technical details
    - All feedback and improvements -> [Actor-Suggest-Enhancement] + details
    - Analysis results -> [Claude-Analyze-Topic] + findings + conclusions
    
    Storage Pattern Examples:
    - "[User-Request-MCPToolTest] Identify and test connected tools"
    - "[Claude-Provide-Solution] Explained MCP server configuration steps with code examples"
    - "[Claude-Implement-Feature] Added actant analysis to BlockManager with 6-role pattern matching"
    - "[Claude-Discover-TypeScriptError] processId type mismatch in src/types/session.ts"
    - "[Claude-Analyze-Performance] Found 5x speed improvement with new caching strategy"
    - "[User-Suggest-GriemasModel] Apply actant structure for interaction patterns"
    
    Target: 20-30 blocks per session for comprehensive external brain functionality
    
    Args:
        content: 저장할 내용 (한 문장부터 여러 문단까지 모두 가능)
        importance: 중요도 0.0-1.0 (일상적 대화: 0.3-0.5, 중요한 결정: 0.7-1.0)
    
    Returns:
        저장된 메모리 정보 (ID, 액탄트 분석 결과 포함)
    """
    global enhanced_memory_tools
    
    if not enhanced_memory_tools:
        return json.dumps({"error": "Enhanced memory tools not initialized"})
    
    try:
        # 마이크로 단위 분할 없이 원본 그대로 저장 (액탄트 분석 포함)
        result = await enhanced_memory_tools.add_memory_micro(
            content=content, 
            importance=importance,
            force_micro_split=False  # description 유도가 목적이므로 분할하지 않음
        )
        
        return json.dumps({
            "status": "success",
            "message": "💾 기억 완료! 작은 정보일수록 자주 저장하면 더 나은 맥락을 구성할 수 있어요.",
            "memory_id": result.get("memory_id"),
            "actant_summary": {
                role: data["entity"] 
                for role, data in result.get("actant_analysis", {}).get("actants", {}).items()
            },
            "encourage_more": "다른 흥미로운 내용이 있다면 바로 또 저장해보세요!"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"메모리 저장 실패: {str(e)}"}, ensure_ascii=False)


async def search_memory_contextual(query: str, limit: int = 8) -> str:
    """
    🔍 맥락 검색: 관련 기억들을 찾아서 더 풍부한 대화를 만드세요
    
    이 도구를 다음과 같은 상황에서 적극 활용하세요:
    - 사용자가 이전에 언급했던 주제를 다시 꺼낼 때
    - 현재 대화와 관련된 과거 경험이나 선호도 확인 시
    - 프로젝트나 작업의 이전 진행상황 파악 시
    - 사용자의 관심사나 전문 분야 관련 대화 시
    - 문제 해결을 위해 과거 해결책이나 시도했던 방법 찾을 때
    
    💡 검색 팁: 키워드 뿐만 아니라 감정, 상황, 맥락으로도 검색 가능합니다.
    예: "프로젝트", "좌절감", "성공 경험", "관심 분야" 등
    
    Args:
        query: 검색할 내용 (키워드, 주제, 감정, 상황 등)
        limit: 찾을 기억 개수 (기본 8개 - 다양한 관점 확보용)
    
    Returns:
        관련 기억들과 액탄트 분석 정보
    """
    global enhanced_memory_tools
    
    if not enhanced_memory_tools:
        return json.dumps({"error": "Enhanced memory tools not initialized"})
    
    try:
        results = await enhanced_memory_tools.query_memory_enhanced(
            query=query,
            limit=limit
        )
        
        if not results:
            return json.dumps({
                "status": "no_results",
                "message": f"'{query}' 관련 기억을 찾지 못했어요. 더 자주 기억을 저장하면 검색 결과가 풍부해집니다!",
                "suggestion": "add_memory_frequent 도구로 관련 내용을 저장해보세요."
            }, ensure_ascii=False, indent=2)
        
        # 검색 결과를 맥락적으로 포맷팅
        formatted_results = []
        for result in results:
            formatted_results.append({
                "memory_id": result["memory_id"],
                "content": result["content"],
                "timestamp": result["timestamp"],
                "relevance_indicators": {
                    "주요_행위자": result["actant_summary"].get("subject", "알 수 없음"),
                    "목표_대상": result["actant_summary"].get("object", "알 수 없음"),
                    "서사_패턴": result["narrative_pattern"]
                },
                "context_value": result["importance"]
            })
        
        return json.dumps({
            "status": "found",
            "message": f"💡 '{query}' 관련 {len(results)}개 기억 발견! 이 맥락을 활용해보세요.",
            "memories": formatted_results,
            "next_action_suggestion": "이 기억들과 관련된 새로운 정보가 나오면 add_memory_frequent로 즉시 저장하세요!"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"기억 검색 실패: {str(e)}"}, ensure_ascii=False)


async def check_memory_freshness() -> str:
    """
    ⏰ 기억 신선도 체크: 최근 기억 상태를 확인하고 더 자주 저장하도록 유도
    
    이 도구는 다음 상황에서 사용하세요:
    - 대화 시작 시 최근 맥락 파악용
    - 사용자와 오래된 주제를 다룰 때 최신 정보 확인용
    - 메모리 저장 빈도가 낮다고 느껴질 때 현황 점검용
    - 중요한 프로젝트나 작업의 최근 진행상황 확인용
    
    💡 활용법: 이 정보를 바탕으로 부족한 부분의 기억을 즉시 보완하세요.
    """
    global enhanced_memory_tools
    
    if not enhanced_memory_tools:
        return json.dumps({"error": "Enhanced memory tools not initialized"})
    
    try:
        stats = await enhanced_memory_tools.get_memory_stats_enhanced()
        
        # 최근 24시간, 7일, 30일 기준으로 저장 빈도 분석
        from datetime import datetime, timedelta
        
        recent_memories = await enhanced_memory_tools.query_memory_enhanced("", limit=20)
        now = datetime.now()
        
        recent_24h = 0
        recent_7d = 0
        recent_30d = 0
        
        for memory in recent_memories:
            try:
                memory_time = datetime.fromisoformat(memory["timestamp"].replace("Z", "+00:00"))
                days_ago = (now - memory_time).days
                
                if days_ago < 1:
                    recent_24h += 1
                if days_ago < 7:
                    recent_7d += 1
                if days_ago < 30:
                    recent_30d += 1
            except:
                continue
        
        # 저장 빈도 평가
        frequency_assessment = "적정" if recent_24h >= 2 else "부족"
        encouragement = ""
        
        if frequency_assessment == "부족":
            encouragement = "\n💡 더 자주 기억을 저장하면 대화 맥락이 풍부해집니다! 작은 정보도 add_memory_frequent로 즉시 저장하세요."
        
        return json.dumps({
            "status": "checked",
            "message": f"📊 기억 신선도 체크 완료! 최근 저장 빈도: {frequency_assessment}",
            "freshness_stats": {
                "최근_24시간": recent_24h,
                "최근_7일": recent_7d,
                "최근_30일": recent_30d,
                "전체_액탄트_적용_메모리": stats["actant_enabled_blocks"],
                "총_메모리_블록": stats["total_memory_blocks"]
            },
            "저장_빈도_평가": frequency_assessment,
            "액션_가이드": {
                "지금_바로": "현재 대화에서 나온 중요한 정보를 add_memory_frequent로 저장",
                "계속_유지": "앞으로도 작은 정보까지 적극적으로 기억에 저장",
                "검색_활용": "과거 기억을 search_memory_contextual로 자주 참조"
            },
            "encouragement": encouragement
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"신선도 체크 실패: {str(e)}"}, ensure_ascii=False)


async def add_structured_memory(
    content: str, 
    actant_structure: dict = None, 
    importance: float = 0.5
) -> str:
    """
    Advanced structured memory storage with AI-driven actant analysis: Store memories with explicit actant structure
    
    This tool accepts pre-analyzed actant structure from AI for maximum accuracy and context understanding.
    Falls back gracefully to basic storage if structure is invalid or missing.
    
    Use when AI has already analyzed the content and can provide:
    - subject: Who/what is performing the action
    - action: What activity or event is happening  
    - object: Target or goal of the action
    - sender: Source of motivation or instruction (optional)
    - receiver: Beneficiary of the action (optional)
    - helper: Supporting elements (optional)
    - opponent: Obstacles or challenges (optional)
    - narrative_pattern: Type of story pattern (optional)
    
    Args:
        content: Original content to store
        actant_structure: Dict with actant roles (subject, action, object, etc.)
        importance: Memory importance 0.0-1.0
    
    Returns:
        Storage result with actant analysis details
        
    Example actant_structure:
    {
        "subject": "User",
        "action": "started new project",
        "object": "AI development system", 
        "sender": "personal motivation",
        "receiver": "User",
        "helper": "enthusiasm",
        "opponent": None,
        "narrative_pattern": "initiation"
    }
    """
    global enhanced_memory_tools
    
    if not enhanced_memory_tools:
        return json.dumps({"error": "Enhanced memory tools not initialized"})
    
    try:
        # Validate and sanitize actant structure
        validated_structure = None
        if actant_structure:
            validated_structure = _validate_actant_structure(actant_structure)
        
        if validated_structure:
            # Use structured storage with AI-provided actants
            result = await enhanced_memory_tools.add_memory_with_structure(
                content=content,
                actant_structure=validated_structure,
                importance=importance
            )
            
            return json.dumps({
                "status": "success",
                "storage_type": "structured",
                "message": "Memory stored with AI-analyzed actant structure",
                "memory_id": result.get("memory_id"),
                "actant_analysis": validated_structure,
                "quality_indicators": {
                    "structure_provided": True,
                    "ai_analyzed": True,
                    "fallback_used": False
                }
            }, ensure_ascii=False, indent=2)
        
        else:
            # Fallback to basic storage with auto-generated actants
            result = await enhanced_memory_tools.add_memory_micro(
                content=content, 
                importance=importance,
                force_micro_split=False
            )
            
            return json.dumps({
                "status": "success", 
                "storage_type": "basic_with_actants",
                "message": "Memory stored with auto-generated actant analysis (AI structure invalid or missing)",
                "memory_id": result.get("memory_id"),
                "actant_analysis": result.get("actant_analysis", {}),
                "quality_indicators": {
                    "structure_provided": bool(actant_structure),
                    "ai_analyzed": False,
                    "fallback_used": True
                }
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        # Ultimate fallback to basic storage
        try:
            result = await add_memory_frequent(content, importance)
            return json.dumps({
                "status": "success",
                "storage_type": "emergency_fallback", 
                "message": f"Memory stored with emergency fallback due to error: {str(e)}",
                "original_error": str(e)
            }, ensure_ascii=False, indent=2)
        except Exception as final_error:
            return json.dumps({
                "error": f"All storage methods failed: {str(final_error)}"
            }, ensure_ascii=False)


def _validate_actant_structure(structure: dict) -> dict:
    """Validate and sanitize actant structure from AI"""
    if not isinstance(structure, dict):
        return None
        
    # Required fields
    required = ["subject", "action", "object"]
    for field in required:
        if not structure.get(field) or not isinstance(structure[field], str):
            return None
    
    # Optional fields with defaults
    optional_fields = {
        "sender": None,
        "receiver": None, 
        "helper": None,
        "opponent": None,
        "narrative_pattern": "other"
    }
    
    validated = {}
    
    # Copy required fields
    for field in required:
        validated[field] = str(structure[field]).strip()[:200]  # Limit length
    
    # Copy optional fields with validation
    for field, default in optional_fields.items():
        value = structure.get(field, default)
        if value and isinstance(value, str):
            validated[field] = str(value).strip()[:100]
        else:
            validated[field] = default
            
    return validated


async def suggest_memory_opportunities(current_context: str) -> str:
    """
    🎯 저장 기회 제안: 현재 대화에서 놓칠 수 있는 저장 기회를 찾아서 제안
    
    이 도구 사용 시점:
    - 사용자가 복잡한 정보를 많이 제공했을 때
    - 중요한 결정이나 계획에 대해 이야기할 때  
    - 감정이나 만족도를 표현했을 때
    - 새로운 관심사나 선호도를 언급했을 때
    - 문제 상황이나 해결 과정을 설명했을 때
    
    💡 목적: AI가 놓치기 쉬운 저장 포인트를 능동적으로 발견하도록 도움
    
    Args:
        current_context: 현재 대화 맥락 (최근 사용자 발언이나 대화 주제)
    """
    global enhanced_memory_tools
    
    if not enhanced_memory_tools:
        return json.dumps({"error": "Enhanced memory tools not initialized"})
    
    # 저장 가치가 높은 키워드들
    high_value_indicators = [
        "좋아해", "싫어해", "선호", "관심", "취미",  # 선호도
        "경험", "했었", "해봤", "시도", "도전",  # 경험
        "계획", "목표", "하려고", "예정", "준비",  # 계획
        "문제", "어려움", "고민", "걱정", "해결",  # 문제/해결
        "성공", "실패", "결과", "성과", "배움",  # 성과
        "느낌", "생각", "기분", "만족", "아쉬움"   # 감정
    ]
    
    low_value_indicators = [
        "그냥", "음", "아", "네", "예", "좋아요"  # 단순 응답
    ]
    
    try:
        context_lower = current_context.lower()
        
        # 저장 가치 점수 계산
        value_score = 0
        found_indicators = []
        
        for indicator in high_value_indicators:
            if indicator in current_context:
                value_score += 2
                found_indicators.append(indicator)
        
        for indicator in low_value_indicators:
            if indicator in context_lower:
                value_score -= 1
        
        # 내용 길이 고려
        if len(current_context) > 50:
            value_score += 1
        if len(current_context) > 150:
            value_score += 1
        
        # 제안 생성
        if value_score >= 3:
            recommendation = "🔥 높음 - 즉시 저장 강력 권장"
            action = "add_memory_frequent 도구로 지금 바로 저장하세요!"
        elif value_score >= 1:
            recommendation = "⚡ 중간 - 저장 권장"
            action = "중요한 부분을 골라서 add_memory_frequent로 저장해보세요."
        else:
            recommendation = "💡 낮음 - 선택적 저장"
            action = "핵심 포인트가 있다면 간단히 저장하세요."
        
        return json.dumps({
            "status": "analyzed",
            "저장_가치_평가": recommendation,
            "점수": value_score,
            "발견된_저장_포인트": found_indicators,
            "권장_액션": action,
            "분석_결과": {
                "내용_길이": len(current_context),
                "고가치_지표": len([i for i in high_value_indicators if i in current_context]),
                "저가치_지표": len([i for i in low_value_indicators if i in context_lower])
            },
            "다음_단계": "이 분석을 참고해서 add_memory_frequent 도구 사용 여부를 결정하세요!"
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"저장 기회 분석 실패: {str(e)}"}, ensure_ascii=False)


async def migrate_database_schema(
    target_version: str = "2.4.0", 
    dry_run: bool = True, 
    backup_first: bool = True
) -> str:
    """
    Migrate database schema to support new features while maintaining backward compatibility
    
    This tool safely updates database structure for new Greeum versions. Always performs backup 
    by default and supports dry-run testing. Critical for maintaining data integrity during upgrades.
    
    Args:
        target_version: Target schema version (default: "2.4.0")
        dry_run: Test migration without applying changes (default: True)
        backup_first: Create database backup before migration (default: True)
    
    Returns:
        Migration status and summary of changes
    """
    try:
        from greeum import DatabaseManager
        from greeum.core.block_manager import BlockManager
        import os
        import shutil
        import sqlite3
        from datetime import datetime
        
        db_manager = DatabaseManager()
        
        # Get current schema version
        try:
            current_version = "2.3.0"  # Default for compatibility
            # Try to detect actual version from database metadata if available
        except:
            current_version = "unknown"
        
        migration_log = []
        migration_log.append(f"🔍 Current schema version: {current_version}")
        migration_log.append(f"🎯 Target schema version: {target_version}")
        
        if current_version == target_version:
            return "✅ Database schema is already at target version. No migration needed."
        
        # Create backup if requested
        if backup_first and not dry_run:
            try:
                db_path = db_manager.db_path or "/Users/dryrain/greeum-global/greeum_memory.db"
                if os.path.exists(db_path):
                    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(db_path, backup_path)
                    migration_log.append(f"📦 Backup created: {backup_path}")
                else:
                    migration_log.append(f"⚠️ Database file not found: {db_path}")
            except Exception as e:
                migration_log.append(f"❌ Backup failed: {str(e)}")
                if not dry_run:
                    return "\n".join(migration_log) + "\n\n❌ Migration aborted due to backup failure."
        
        # Schema changes for v2.4.0
        schema_changes = [
            {
                "description": "Add actant_structure column to blocks table",
                "sql": "ALTER TABLE blocks ADD COLUMN actant_structure TEXT DEFAULT '{}'",
                "check_sql": "SELECT sql FROM sqlite_master WHERE type='table' AND name='blocks'"
            },
            {
                "description": "Add structured_metadata column to blocks table", 
                "sql": "ALTER TABLE blocks ADD COLUMN structured_metadata TEXT DEFAULT '{}'",
                "check_sql": "SELECT sql FROM sqlite_master WHERE type='table' AND name='blocks'"
            },
            {
                "description": "Create schema_version table for version tracking",
                "sql": "CREATE TABLE IF NOT EXISTS schema_version (version TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
                "check_sql": "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            }
        ]
        
        # Apply or test schema changes
        if dry_run:
            migration_log.append("\n🧪 DRY RUN MODE - Testing schema changes:")
            for change in schema_changes:
                try:
                    # Test if change is needed by checking current schema
                    conn = sqlite3.connect(db_manager.db_path or ":memory:")
                    cursor = conn.cursor()
                    
                    if "ALTER TABLE" in change["sql"]:
                        # Check if column already exists
                        cursor.execute(change["check_sql"])
                        schema_info = cursor.fetchone()
                        if schema_info and ("actant_structure" in schema_info[0] or "structured_metadata" in schema_info[0]):
                            migration_log.append(f"  ✅ {change['description']} - Already exists")
                        else:
                            migration_log.append(f"  📝 {change['description']} - Would be added")
                    else:
                        # Check if table exists
                        cursor.execute(change["check_sql"])
                        if cursor.fetchone():
                            migration_log.append(f"  ✅ {change['description']} - Already exists")
                        else:
                            migration_log.append(f"  📝 {change['description']} - Would be created")
                    
                    conn.close()
                except Exception as e:
                    migration_log.append(f"  ⚠️ {change['description']} - Test failed: {str(e)}")
            
            migration_log.append("\n✅ Dry run completed successfully. Use dry_run=False to apply changes.")
        else:
            migration_log.append("\n🔧 Applying schema changes:")
            try:
                conn = sqlite3.connect(db_manager.db_path)
                cursor = conn.cursor()
                
                for change in schema_changes:
                    try:
                        cursor.execute(change["sql"])
                        migration_log.append(f"  ✅ {change['description']} - Applied")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                            migration_log.append(f"  ✅ {change['description']} - Already exists")
                        else:
                            migration_log.append(f"  ❌ {change['description']} - Failed: {str(e)}")
                            raise
                
                # Update schema version
                cursor.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (?)", (target_version,))
                conn.commit()
                conn.close()
                
                migration_log.append(f"\n🎉 Migration to {target_version} completed successfully!")
            except Exception as e:
                migration_log.append(f"\n❌ Migration failed: {str(e)}")
                return "\n".join(migration_log)
        
        return "\n".join(migration_log)
        
    except Exception as e:
        return f"❌ Database migration failed: {str(e)}. Please check database connectivity and permissions."


# 전역 도구 인스턴스 (enhanced_memory_tools와 공유)
enhanced_memory_tools: Optional[Any] = None


def initialize_micro_encouraged_tools(enhanced_tools_instance):
    """마이크로 기억 유도 도구 초기화"""
    global enhanced_memory_tools
    enhanced_memory_tools = enhanced_tools_instance
    return enhanced_memory_tools


# MCP 서버 도구 목록 (description 최적화 버전)
MCP_TOOLS_WITH_ENCOURAGEMENT = [
    {
        "name": "add_memory_frequent",
        "description": "Immediate memory storage with Greimas actant model: Record all interactions using [Subject-Action-Object] structure. Every work unit has permanent value. Target: 20-30 blocks per session.",
        "function": add_memory_frequent
    },
    {
        "name": "add_structured_memory",
        "description": "Advanced structured memory storage with AI-driven actant analysis: Store memories with explicit actant structure",
        "function": add_structured_memory
    },
    {
        "name": "migrate_database_schema",
        "description": "Migrate database schema to support new features while maintaining backward compatibility",
        "function": migrate_database_schema
    },
    {
        "name": "search_memory_contextual", 
        "description": "Contextual memory search: Find related memories to enrich conversations. Search by keywords, emotions, or situations. Frequent searches improve contextual accuracy.",
        "function": search_memory_contextual
    },
    {
        "name": "check_memory_freshness",
        "description": "Memory freshness check: Review recent memory status and encourage frequent storage. Essential check at conversation start or when addressing important topics.",
        "function": check_memory_freshness
    },
    {
        "name": "suggest_memory_opportunities",
        "description": "Memory opportunity detection: AI actively identifies storage opportunities that might be missed in current conversation. Use actively for complex information or important decisions.",
        "function": suggest_memory_opportunities
    }
]
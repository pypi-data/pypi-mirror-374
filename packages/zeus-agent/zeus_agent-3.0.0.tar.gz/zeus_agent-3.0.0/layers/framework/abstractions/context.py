"""
Context Abstractions - 上下文抽象
支持通用上下文和团队上下文
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class UniversalContext:
    """通用上下文"""
    data: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文数据"""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置上下文数据"""
        self.data[key] = value
    
    def update(self, data: Dict[str, Any]) -> None:
        """更新上下文数据"""
        self.data.update(data)
    
    def clear(self) -> None:
        """清空上下文数据"""
        self.data.clear()
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有上下文数据"""
        return self.data.copy()
    
    def copy(self) -> 'UniversalContext':
        """创建上下文副本"""
        return UniversalContext(
            data=self.data.copy(),
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=self.timestamp
        )


@dataclass
class TeamContext:
    """团队上下文"""
    team_name: str
    current_round: int = 0
    participants: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    shared_state: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_participant(self, name: str) -> Optional[str]:
        """获取参与者"""
        return name if name in self.participants else None
    
    def add_participant(self, name: str) -> None:
        """添加参与者"""
        if name not in self.participants:
            self.participants.append(name)
    
    def remove_participant(self, name: str) -> None:
        """移除参与者"""
        if name in self.participants:
            self.participants.remove(name)
    
    def add_conversation(self, speaker: str, message: str, round_num: int) -> None:
        """添加对话记录"""
        self.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "round": round_num,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_conversation_history(self, speaker: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取对话历史"""
        if speaker:
            return [msg for msg in self.conversation_history if msg["speaker"] == speaker]
        return self.conversation_history
    
    def set_shared_state(self, key: str, value: Any) -> None:
        """设置共享状态"""
        self.shared_state[key] = value
    
    def get_shared_state(self, key: str, default: Any = None) -> Any:
        """获取共享状态"""
        return self.shared_state.get(key, default)
    
    def clear_shared_state(self) -> None:
        """清空共享状态"""
        self.shared_state.clear() 
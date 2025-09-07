"""
安全管理系统
支持工具沙盒、Prompt注入防护、隐私数据保护、访问控制
"""

import re
import hashlib
import secrets
import threading
from typing import Dict, Any, List, Optional, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import subprocess
import tempfile
import os
from pathlib import Path


class SecurityLevel(Enum):
    """安全级别枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """威胁类型枚举"""
    PROMPT_INJECTION = "prompt_injection"
    DATA_LEAK = "data_leak"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALICIOUS_CODE = "malicious_code"
    RESOURCE_ABUSE = "resource_abuse"


@dataclass
class SecurityEvent:
    """安全事件"""
    id: str
    timestamp: float
    threat_type: ThreatType
    level: SecurityLevel
    source: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    blocked: bool = False
    user_id: Optional[str] = None


@dataclass
class SandboxConfig:
    """沙盒配置"""
    max_execution_time: float = 30.0
    max_memory_mb: int = 512
    allowed_modules: Set[str] = field(default_factory=set)
    blocked_modules: Set[str] = field(default_factory=set)
    allowed_file_paths: Set[str] = field(default_factory=set)
    network_access: bool = False
    temp_dir_only: bool = True


class PromptInjectionDetector:
    """Prompt注入检测器"""
    
    def __init__(self):
        # 危险模式列表
        self.dangerous_patterns = [
            # 直接指令注入
            r"(?i)(ignore|forget|disregard)\s+(previous|above|all)\s+(instructions?|rules?|prompts?)",
            r"(?i)system\s*:\s*you\s+are\s+now",
            r"(?i)(act|behave|pretend)\s+as\s+(if\s+you\s+are|a)",
            
            # 角色劫持
            r"(?i)you\s+are\s+now\s+(a|an)\s+\w+",
            r"(?i)from\s+now\s+on,?\s+you\s+(are|will\s+be)",
            r"(?i)new\s+(role|character|persona|identity)",
            
            # 系统提示泄露
            r"(?i)(show|reveal|display|tell\s+me)\s+(your|the)\s+(system\s+)?(prompt|instructions?)",
            r"(?i)what\s+(are\s+)?your\s+(initial\s+)?(instructions?|rules?|guidelines?)",
            
            # 绕过限制
            r"(?i)(override|bypass|circumvent)\s+(security|safety|restrictions?)",
            r"(?i)in\s+(developer|debug|admin)\s+mode",
            
            # 代码执行尝试
            r"(?i)(execute|run|eval)\s+(code|script|command)",
            r"(?i)```\s*(python|javascript|bash|shell)",
            
            # 数据提取
            r"(?i)(extract|dump|export)\s+(data|information|content)",
            r"(?i)list\s+all\s+(files|users|passwords?|secrets?)"
        ]
        
        # 编译正则表达式
        self.compiled_patterns = [re.compile(pattern) for pattern in self.dangerous_patterns]
        
        # 可疑关键词
        self.suspicious_keywords = {
            'system', 'admin', 'root', 'sudo', 'password', 'secret', 'token',
            'override', 'bypass', 'hack', 'exploit', 'inject', 'execute'
        }
    
    def detect(self, text: str) -> Dict[str, Any]:
        """检测Prompt注入"""
        if not text:
            return {'is_malicious': False, 'confidence': 0.0, 'reasons': []}
        
        reasons = []
        confidence = 0.0
        
        # 模式匹配检测
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text.lower())
            if matches:
                reasons.append(f"匹配危险模式 {i+1}: {matches[0]}")
                confidence += 0.3
        
        # 关键词密度检测
        words = set(re.findall(r'\b\w+\b', text.lower()))
        suspicious_count = len(words.intersection(self.suspicious_keywords))
        if suspicious_count > 2:
            reasons.append(f"包含 {suspicious_count} 个可疑关键词")
            confidence += suspicious_count * 0.1
        
        # 长度异常检测
        if len(text) > 5000:
            reasons.append("文本长度异常")
            confidence += 0.1
        
        # 特殊字符检测
        special_chars = len(re.findall(r'[<>{}[\]()";\\]', text))
        if special_chars > len(text) * 0.1:
            reasons.append("包含过多特殊字符")
            confidence += 0.2
        
        confidence = min(confidence, 1.0)
        is_malicious = confidence > 0.5
        
        return {
            'is_malicious': is_malicious,
            'confidence': confidence,
            'reasons': reasons,
            'suspicious_keywords': list(words.intersection(self.suspicious_keywords))
        }


class DataPrivacyProtector:
    """数据隐私保护器"""
    
    def __init__(self):
        # 敏感数据模式
        self.sensitive_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b|\b\d{10}\b|\+\d{1,3}\s?\d{3,4}\s?\d{3,4}\s?\d{3,4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',
            'password': r'(?i)(password|pwd|pass)\s*[=:]\s*["\']?([^"\'\s]+)["\']?'
        }
        
        self.compiled_patterns = {
            name: re.compile(pattern) 
            for name, pattern in self.sensitive_patterns.items()
        }
    
    def scan_text(self, text: str) -> Dict[str, List[str]]:
        """扫描文本中的敏感数据"""
        findings = {}
        
        for data_type, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            if matches:
                if data_type == 'password':
                    # 密码模式返回元组，只取密码部分
                    matches = [match[1] if isinstance(match, tuple) else match for match in matches]
                findings[data_type] = matches
        
        return findings
    
    def anonymize_text(self, text: str) -> str:
        """匿名化文本中的敏感数据"""
        anonymized = text
        
        # 替换敏感数据
        for data_type, pattern in self.compiled_patterns.items():
            if data_type == 'email':
                anonymized = pattern.sub('***@***.***', anonymized)
            elif data_type == 'phone':
                anonymized = pattern.sub('***-***-****', anonymized)
            elif data_type == 'ssn':
                anonymized = pattern.sub('***-**-****', anonymized)
            elif data_type == 'credit_card':
                anonymized = pattern.sub('****-****-****-****', anonymized)
            elif data_type == 'ip_address':
                anonymized = pattern.sub('***.***.***.***', anonymized)
            elif data_type == 'api_key':
                anonymized = pattern.sub('***API_KEY***', anonymized)
            elif data_type == 'password':
                anonymized = pattern.sub(r'\1=***REDACTED***', anonymized)
        
        return anonymized
    
    def generate_data_hash(self, data: str) -> str:
        """生成数据哈希用于追踪"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class ToolSandbox:
    """工具执行沙盒"""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._temp_dirs: List[str] = []
    
    def execute_safe(self, code: str, language: str = "python") -> Dict[str, Any]:
        """安全执行代码"""
        if language.lower() != "python":
            return {
                'success': False,
                'error': f"不支持的语言: {language}",
                'output': '',
                'execution_time': 0.0
            }
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        self._temp_dirs.append(temp_dir)
        
        try:
            # 创建安全的Python脚本
            safe_code = self._create_safe_code(code)
            script_path = os.path.join(temp_dir, "script.py")
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(safe_code)
            
            # 执行代码
            result = self._execute_with_limits(script_path, temp_dir)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': 0.0
            }
        finally:
            # 清理临时目录
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                if temp_dir in self._temp_dirs:
                    self._temp_dirs.remove(temp_dir)
            except:
                pass
    
    def _create_safe_code(self, original_code: str) -> str:
        """创建安全的代码包装器"""
        # 检查危险导入
        dangerous_imports = [
            'os', 'sys', 'subprocess', 'shutil', 'glob', 'socket',
            'urllib', 'requests', 'http', 'ftplib', 'smtplib'
        ]
        
        lines = original_code.split('\n')
        safe_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查危险导入
            if line_stripped.startswith(('import ', 'from ')):
                for dangerous in dangerous_imports:
                    if dangerous in line_stripped and dangerous not in self.config.allowed_modules:
                        if dangerous not in self.config.blocked_modules:
                            self.config.blocked_modules.add(dangerous)
                        continue
            
            # 检查危险函数调用
            dangerous_calls = ['exec(', 'eval(', 'compile(', '__import__(']
            if any(call in line for call in dangerous_calls):
                safe_lines.append(f"# 危险调用已被阻止: {line}")
                continue
            
            safe_lines.append(line)
        
        # 添加资源限制
        wrapper = f"""
import sys
import signal
import traceback
from io import StringIO

# 重定向输出
old_stdout = sys.stdout
sys.stdout = StringIO()

# 设置执行时间限制
def timeout_handler(signum, frame):
    raise TimeoutError("执行超时")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({int(self.config.max_execution_time)})

try:
    # 用户代码开始
{chr(10).join('    ' + line for line in safe_lines)}
    # 用户代码结束
    
    result = sys.stdout.getvalue()
    print("EXECUTION_SUCCESS:", result)
    
except Exception as e:
    print("EXECUTION_ERROR:", str(e))
    print("TRACEBACK:", traceback.format_exc())
finally:
    signal.alarm(0)  # 取消定时器
    sys.stdout = old_stdout
"""
        return wrapper
    
    def _execute_with_limits(self, script_path: str, work_dir: str) -> Dict[str, Any]:
        """执行代码并限制资源"""
        import time
        start_time = time.time()
        
        try:
            # 使用subprocess执行，设置资源限制
            result = subprocess.run([
                'python3', script_path
            ], 
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=self.config.max_execution_time,
            # 限制内存使用（在支持的系统上）
            # preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (self.config.max_memory_mb * 1024 * 1024, -1))
            )
            
            execution_time = time.time() - start_time
            
            # 解析输出
            stdout = result.stdout
            stderr = result.stderr
            
            if "EXECUTION_SUCCESS:" in stdout:
                output = stdout.split("EXECUTION_SUCCESS:", 1)[1].strip()
                return {
                    'success': True,
                    'output': output,
                    'error': '',
                    'execution_time': execution_time
                }
            elif "EXECUTION_ERROR:" in stdout:
                error = stdout.split("EXECUTION_ERROR:", 1)[1].strip()
                return {
                    'success': False,
                    'output': '',
                    'error': error,
                    'execution_time': execution_time
                }
            else:
                return {
                    'success': False,
                    'output': stdout,
                    'error': stderr,
                    'execution_time': execution_time
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f"执行超时 ({self.config.max_execution_time}s)",
                'output': '',
                'execution_time': self.config.max_execution_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'execution_time': time.time() - start_time
            }


class SecurityManager:
    """安全管理器主类"""
    
    def __init__(self):
        self.injection_detector = PromptInjectionDetector()
        self.privacy_protector = DataPrivacyProtector()
        self.events: List[SecurityEvent] = []
        self.handlers: List[Callable[[SecurityEvent], None]] = []
        self._lock = threading.RLock()
        
        # 默认沙盒配置
        self.default_sandbox_config = SandboxConfig(
            allowed_modules={'math', 'random', 'datetime', 'json', 're'},
            blocked_modules={'os', 'sys', 'subprocess', 'socket'},
            max_execution_time=10.0,
            max_memory_mb=128
        )
    
    def add_security_handler(self, handler: Callable[[SecurityEvent], None]):
        """添加安全事件处理器"""
        self.handlers.append(handler)
    
    def check_prompt_injection(self, text: str, user_id: Optional[str] = None) -> bool:
        """检查Prompt注入攻击"""
        detection_result = self.injection_detector.detect(text)
        
        if detection_result['is_malicious']:
            event = SecurityEvent(
                id=self._generate_event_id(),
                timestamp=time.time(),
                threat_type=ThreatType.PROMPT_INJECTION,
                level=SecurityLevel.HIGH if detection_result['confidence'] > 0.8 else SecurityLevel.MEDIUM,
                source="prompt_injection_detector",
                description=f"检测到Prompt注入攻击: {', '.join(detection_result['reasons'])}",
                data=detection_result,
                blocked=True,
                user_id=user_id
            )
            
            self._log_security_event(event)
            return True
        
        return False
    
    def scan_for_sensitive_data(self, text: str, user_id: Optional[str] = None) -> Dict[str, List[str]]:
        """扫描敏感数据"""
        findings = self.privacy_protector.scan_text(text)
        
        if findings:
            event = SecurityEvent(
                id=self._generate_event_id(),
                timestamp=time.time(),
                threat_type=ThreatType.DATA_LEAK,
                level=SecurityLevel.MEDIUM,
                source="privacy_protector",
                description=f"检测到敏感数据: {list(findings.keys())}",
                data={'findings': findings},
                blocked=False,
                user_id=user_id
            )
            
            self._log_security_event(event)
        
        return findings
    
    def anonymize_text(self, text: str) -> str:
        """匿名化敏感数据"""
        return self.privacy_protector.anonymize_text(text)
    
    def create_sandbox(self, config: Optional[SandboxConfig] = None) -> ToolSandbox:
        """创建工具沙盒"""
        config = config or self.default_sandbox_config
        return ToolSandbox(config)
    
    def execute_code_safely(self, code: str, language: str = "python", 
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """安全执行代码"""
        # 检查代码中的安全问题
        if self.check_prompt_injection(code, user_id):
            return {
                'success': False,
                'error': '代码包含潜在的安全威胁',
                'output': '',
                'execution_time': 0.0
            }
        
        # 在沙盒中执行
        sandbox = self.create_sandbox()
        result = sandbox.execute_safe(code, language)
        
        # 记录执行事件
        event = SecurityEvent(
            id=self._generate_event_id(),
            timestamp=time.time(),
            threat_type=ThreatType.MALICIOUS_CODE,
            level=SecurityLevel.LOW if result['success'] else SecurityLevel.MEDIUM,
            source="code_executor",
            description=f"代码执行{'成功' if result['success'] else '失败'}: {language}",
            data={'result': result, 'code_length': len(code)},
            blocked=not result['success'],
            user_id=user_id
        )
        
        self._log_security_event(event)
        return result
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        return f"sec_{int(time.time())}_{secrets.token_hex(4)}"
    
    def _log_security_event(self, event: SecurityEvent):
        """记录安全事件"""
        with self._lock:
            self.events.append(event)
            
            # 保持最近1000个事件
            if len(self.events) > 1000:
                self.events = self.events[-1000:]
            
            # 调用处理器
            for handler in self.handlers:
                try:
                    handler(event)
                except Exception as e:
                    print(f"安全事件处理器执行失败: {e}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """获取安全统计信息"""
        with self._lock:
            if not self.events:
                return {
                    'total_events': 0,
                    'events_by_type': {},
                    'events_by_level': {},
                    'blocked_events': 0,
                    'recent_events': []
                }
            
            # 统计事件类型
            events_by_type = {}
            events_by_level = {}
            blocked_count = 0
            
            for event in self.events:
                events_by_type[event.threat_type.value] = \
                    events_by_type.get(event.threat_type.value, 0) + 1
                events_by_level[event.level.value] = \
                    events_by_level.get(event.level.value, 0) + 1
                
                if event.blocked:
                    blocked_count += 1
            
            # 最近的事件
            recent_events = [
                {
                    'id': event.id,
                    'timestamp': event.timestamp,
                    'type': event.threat_type.value,
                    'level': event.level.value,
                    'description': event.description,
                    'blocked': event.blocked
                }
                for event in self.events[-10:]  # 最近10个事件
            ]
            
            return {
                'total_events': len(self.events),
                'events_by_type': events_by_type,
                'events_by_level': events_by_level,
                'blocked_events': blocked_count,
                'block_rate': blocked_count / len(self.events) if self.events else 0,
                'recent_events': recent_events
            }


# 全局安全管理器实例
_global_security_manager = None


def get_security_manager() -> SecurityManager:
    """获取全局安全管理器"""
    global _global_security_manager
    
    if _global_security_manager is None:
        _global_security_manager = SecurityManager()
    
    return _global_security_manager


# 便捷函数
def check_security(text: str, user_id: Optional[str] = None) -> bool:
    """检查文本安全性"""
    manager = get_security_manager()
    return not manager.check_prompt_injection(text, user_id)


def anonymize_data(text: str) -> str:
    """匿名化敏感数据"""
    return get_security_manager().anonymize_text(text)


def execute_code_safely(code: str, language: str = "python", user_id: Optional[str] = None) -> Dict[str, Any]:
    """安全执行代码"""
    return get_security_manager().execute_code_safely(code, language, user_id) 
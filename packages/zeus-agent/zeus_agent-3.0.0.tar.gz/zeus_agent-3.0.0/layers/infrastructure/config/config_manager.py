"""
智能配置管理系统
支持多环境配置、动态重载、配置验证、敏感信息加密
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import threading
from datetime import datetime
import hashlib
import base64
from cryptography.fernet import Fernet


class ConfigFormat(Enum):
    """配置文件格式枚举"""
    YAML = "yaml"
    JSON = "json"
    ENV = "env"


class ConfigSource(Enum):
    """配置源枚举"""
    FILE = "file"
    ENVIRONMENT = "environment"
    REMOTE = "remote"
    MEMORY = "memory"


@dataclass
class ConfigSchema:
    """配置模式定义"""
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    field_types: Dict[str, type] = field(default_factory=dict)
    validators: Dict[str, Callable] = field(default_factory=dict)
    encrypted_fields: List[str] = field(default_factory=list)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class ConfigManager:
    """智能配置管理器"""
    
    def __init__(self, 
                 config_dir: str = "config",
                 environment: str = "development",
                 auto_reload: bool = True,
                 encryption_key: Optional[str] = None):
        
        self.config_dir = Path(config_dir)
        self.environment = environment
        self.auto_reload = auto_reload
        
        # 配置存储
        self._config_data: Dict[str, Any] = {}
        self._file_timestamps: Dict[str, float] = {}
        self._schemas: Dict[str, ConfigSchema] = {}
        self._watchers: List[Callable] = []
        
        # 线程安全
        self._lock = threading.RLock()
        
        # 加密支持
        self._cipher = None
        if encryption_key:
            self._cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) 
                                else encryption_key)
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self._load_all_configs()
    
    def register_schema(self, namespace: str, schema: ConfigSchema):
        """注册配置模式"""
        with self._lock:
            self._schemas[namespace] = schema
    
    def add_watcher(self, callback: Callable[[str, Dict[str, Any]], None]):
        """添加配置变更监听器"""
        self._watchers.append(callback)
    
    def _notify_watchers(self, namespace: str, config: Dict[str, Any]):
        """通知配置变更监听器"""
        for watcher in self._watchers:
            try:
                watcher(namespace, config)
            except Exception as e:
                print(f"配置监听器执行失败: {e}")
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        # 加载基础配置
        self._load_config_file("default")
        
        # 加载环境特定配置
        if self.environment != "default":
            self._load_config_file(self.environment)
        
        # 加载环境变量
        self._load_environment_variables()
    
    def _load_config_file(self, name: str):
        """加载指定配置文件"""
        for ext in ["yaml", "yml", "json"]:
            config_file = self.config_dir / f"{name}.{ext}"
            if config_file.exists():
                try:
                    with self._lock:
                        config_data = self._read_config_file(config_file)
                        self._merge_config(name, config_data)
                        self._file_timestamps[str(config_file)] = config_file.stat().st_mtime
                    
                    print(f"已加载配置文件: {config_file}")
                    return
                except Exception as e:
                    print(f"配置文件加载失败 {config_file}: {e}")
    
    def _read_config_file(self, file_path: Path) -> Dict[str, Any]:
        """读取配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif file_path.suffix.lower() == '.json':
                return json.load(f)
            else:
                raise ValueError(f"不支持的配置文件格式: {file_path.suffix}")
    
    def _load_environment_variables(self):
        """从环境变量加载配置"""
        env_config = {}
        
        # 查找所有以ADC_开头的环境变量
        for key, value in os.environ.items():
            if key.startswith('ADC_'):
                # 转换为嵌套字典格式
                config_key = key[4:].lower().replace('_', '.')
                self._set_nested_value(env_config, config_key, self._parse_env_value(value))
        
        if env_config:
            with self._lock:
                self._merge_config("environment", env_config)
    
    def _parse_env_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为JSON
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
        
        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试解析为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 返回字符串
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any):
        """设置嵌套字典值"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _merge_config(self, namespace: str, new_config: Dict[str, Any]):
        """合并配置"""
        if namespace not in self._config_data:
            self._config_data[namespace] = {}
        
        self._deep_merge(self._config_data[namespace], new_config)
        
        # 解密敏感字段
        if namespace in self._schemas:
            self._decrypt_fields(namespace, self._config_data[namespace])
        
        # 验证配置
        self._validate_config(namespace, self._config_data[namespace])
        
        # 通知监听器
        self._notify_watchers(namespace, self._config_data[namespace])
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]):
        """深度合并字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _decrypt_fields(self, namespace: str, config: Dict[str, Any]):
        """解密敏感字段"""
        if not self._cipher or namespace not in self._schemas:
            return
        
        schema = self._schemas[namespace]
        for field in schema.encrypted_fields:
            if field in config:
                try:
                    encrypted_value = config[field]
                    if isinstance(encrypted_value, str) and encrypted_value.startswith('enc:'):
                        decrypted = self._cipher.decrypt(
                            base64.b64decode(encrypted_value[4:])
                        ).decode()
                        config[field] = decrypted
                except Exception as e:
                    print(f"字段解密失败 {field}: {e}")
    
    def _validate_config(self, namespace: str, config: Dict[str, Any]):
        """验证配置"""
        if namespace not in self._schemas:
            return
        
        schema = self._schemas[namespace]
        
        # 检查必需字段
        for field in schema.required_fields:
            if field not in config:
                raise ConfigValidationError(f"缺少必需配置字段: {field}")
        
        # 检查字段类型
        for field, expected_type in schema.field_types.items():
            if field in config and not isinstance(config[field], expected_type):
                raise ConfigValidationError(
                    f"配置字段 {field} 类型错误，期望 {expected_type.__name__}，"
                    f"实际 {type(config[field]).__name__}"
                )
        
        # 执行自定义验证器
        for field, validator in schema.validators.items():
            if field in config:
                try:
                    if not validator(config[field]):
                        raise ConfigValidationError(f"配置字段 {field} 验证失败")
                except Exception as e:
                    raise ConfigValidationError(f"配置字段 {field} 验证异常: {e}")
    
    def get(self, key: str, default: Any = None, namespace: str = None) -> Any:
        """获取配置值"""
        with self._lock:
            # 检查是否需要重新加载
            if self.auto_reload:
                self._check_and_reload()
            
            # 确定搜索的命名空间
            if namespace:
                namespaces = [namespace]
            else:
                namespaces = [self.environment, "default"]
            
            # 在命名空间中搜索配置
            for ns in namespaces:
                if ns in self._config_data:
                    value = self._get_nested_value(self._config_data[ns], key)
                    if value is not None:
                        return value
            
            return default
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """获取嵌套配置值"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def set(self, key: str, value: Any, namespace: str = None, encrypt: bool = False):
        """设置配置值"""
        if namespace is None:
            namespace = self.environment
        
        with self._lock:
            if namespace not in self._config_data:
                self._config_data[namespace] = {}
            
            # 加密敏感值
            if encrypt and self._cipher:
                encrypted = base64.b64encode(
                    self._cipher.encrypt(str(value).encode())
                ).decode()
                value = f"enc:{encrypted}"
            
            self._set_nested_value(self._config_data[namespace], key, value)
            
            # 通知监听器
            self._notify_watchers(namespace, self._config_data[namespace])
    
    def get_all(self, namespace: str = None) -> Dict[str, Any]:
        """获取所有配置"""
        with self._lock:
            if namespace:
                return self._config_data.get(namespace, {}).copy()
            else:
                # 合并所有命名空间的配置
                merged = {}
                for ns in ["default", self.environment]:
                    if ns in self._config_data:
                        self._deep_merge(merged, self._config_data[ns])
                return merged
    
    def _check_and_reload(self):
        """检查并重新加载配置文件"""
        for file_path, last_mtime in self._file_timestamps.items():
            path = Path(file_path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                if current_mtime > last_mtime:
                    print(f"检测到配置文件变更: {file_path}")
                    # 重新加载特定文件
                    name = path.stem
                    try:
                        config_data = self._read_config_file(path)
                        self._merge_config(name, config_data)
                        self._file_timestamps[file_path] = current_mtime
                    except Exception as e:
                        print(f"重新加载配置文件失败 {file_path}: {e}")
    
    def reload(self):
        """手动重新加载所有配置"""
        with self._lock:
            self._config_data.clear()
            self._file_timestamps.clear()
            self._load_all_configs()
            print("配置已重新加载")
    
    def save_to_file(self, namespace: str, file_path: Optional[str] = None):
        """保存配置到文件"""
        if namespace not in self._config_data:
            raise ValueError(f"命名空间 {namespace} 不存在")
        
        if file_path is None:
            file_path = self.config_dir / f"{namespace}.yaml"
        
        config_to_save = self._config_data[namespace].copy()
        
        # 加密敏感字段
        if namespace in self._schemas:
            schema = self._schemas[namespace]
            for field in schema.encrypted_fields:
                if field in config_to_save and not str(config_to_save[field]).startswith('enc:'):
                    if self._cipher:
                        encrypted = base64.b64encode(
                            self._cipher.encrypt(str(config_to_save[field]).encode())
                        ).decode()
                        config_to_save[field] = f"enc:{encrypted}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_to_save, f, default_flow_style=False, allow_unicode=True)
        
        print(f"配置已保存到: {file_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取配置管理统计信息"""
        with self._lock:
            return {
                'environment': self.environment,
                'config_dir': str(self.config_dir),
                'namespaces': list(self._config_data.keys()),
                'total_configs': sum(len(config) for config in self._config_data.values()),
                'schemas_registered': len(self._schemas),
                'watchers_count': len(self._watchers),
                'files_watched': len(self._file_timestamps),
                'auto_reload': self.auto_reload
            }


# 全局配置管理器实例
_global_config_manager = None


def get_config_manager(**kwargs) -> ConfigManager:
    """获取全局配置管理器"""
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = ConfigManager(**kwargs)
    
    return _global_config_manager


def get_config(key: str, default: Any = None, namespace: str = None) -> Any:
    """获取配置值的便捷函数"""
    return get_config_manager().get(key, default, namespace)


def set_config(key: str, value: Any, namespace: str = None, encrypt: bool = False):
    """设置配置值的便捷函数"""
    get_config_manager().set(key, value, namespace, encrypt)


# 生成加密密钥的工具函数
def generate_encryption_key() -> str:
    """生成新的加密密钥"""
    return Fernet.generate_key().decode()


# 常用配置模式
DEEPSEEK_SCHEMA = ConfigSchema(
    required_fields=['api_key', 'base_url', 'model'],
    optional_fields=['max_tokens', 'temperature', 'top_p', 'timeout'],
    field_types={
        'api_key': str,
        'base_url': str,
        'model': str,
        'max_tokens': int,
        'temperature': float,
        'top_p': float,
        'timeout': int
    },
    encrypted_fields=['api_key'],
    validators={
        'temperature': lambda x: 0 <= x <= 2,
        'top_p': lambda x: 0 <= x <= 1,
        'max_tokens': lambda x: x > 0
    }
)

LOGGING_SCHEMA = ConfigSchema(
    required_fields=['level'],
    optional_fields=['file', 'max_size', 'backup_count', 'format'],
    field_types={
        'level': str,
        'file': str,
        'max_size': str,
        'backup_count': int,
        'format': str
    },
    validators={
        'level': lambda x: x.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    }
) 
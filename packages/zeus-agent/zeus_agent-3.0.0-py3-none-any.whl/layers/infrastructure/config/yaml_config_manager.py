"""
YAML配置管理器
提供配置驱动的Agent开发框架

特性：
- 支持多层级配置继承
- 环境变量替换
- 配置验证和类型检查
- 热重载支持
- 配置模板系统
"""

import os
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import yaml
from yaml.loader import SafeLoader
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ConfigMetadata:
    """配置元数据"""
    name: str
    version: str
    description: str = ""
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"


@dataclass
class ConfigValidationResult:
    """配置验证结果"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class EnvironmentVariableLoader(SafeLoader):
    """支持环境变量的YAML加载器"""
    pass


def env_var_constructor(loader, node):
    """环境变量构造器"""
    value = loader.construct_scalar(node)
    
    # 支持默认值: ${VAR_NAME:default_value}
    if ':' in value:
        var_name, default_value = value.split(':', 1)
        return os.getenv(var_name, default_value)
    else:
        env_value = os.getenv(value)
        if env_value is None:
            raise ValueError(f"环境变量 {value} 未设置")
        return env_value


# 注册环境变量构造器
EnvironmentVariableLoader.add_constructor('!env', env_var_constructor)


class YAMLConfigManager:
    """
    YAML配置管理器
    
    支持：
    - 多层级配置继承
    - 环境变量替换
    - 配置验证
    - 热重载
    - 配置模板
    """
    
    def __init__(self, 
                 config_dir: str = "./config",
                 schema_dir: str = "./config/schemas",
                 template_dir: str = "./config/templates"):
        """初始化配置管理器"""
        self.config_dir = Path(config_dir)
        self.schema_dir = Path(schema_dir)
        self.template_dir = Path(template_dir)
        
        # 确保目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.schema_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置缓存
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
        self._file_timestamps: Dict[str, float] = {}
        
        logger.info(f"🔧 初始化YAML配置管理器: {config_dir}")
    
    def load_config(self, 
                    config_name: str,
                    environment: str = "development",
                    validate_schema: bool = True,
                    use_cache: bool = True) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_name: 配置名称（不含扩展名）
            environment: 环境名称
            validate_schema: 是否验证schema
            use_cache: 是否使用缓存
            
        Returns:
            配置字典
        """
        cache_key = f"{config_name}_{environment}"
        
        # 检查缓存
        if use_cache and cache_key in self._config_cache:
            if not self._is_config_changed(config_name, environment):
                logger.debug(f"📋 使用缓存配置: {cache_key}")
                return self._config_cache[cache_key]
        
        logger.info(f"📖 加载配置: {config_name} (环境: {environment})")
        
        try:
            # 1. 加载基础配置
            base_config = self._load_base_config(config_name)
            
            # 2. 加载环境特定配置
            env_config = self._load_environment_config(config_name, environment)
            
            # 3. 合并配置
            merged_config = self._merge_configs(base_config, env_config)
            
            # 4. 处理继承
            if 'extends' in merged_config:
                parent_config = self.load_config(
                    merged_config['extends'], 
                    environment, 
                    validate_schema=False,
                    use_cache=use_cache
                )
                merged_config = self._merge_configs(parent_config, merged_config)
                del merged_config['extends']  # 移除继承标记
            
            # 5. 处理环境变量替换
            merged_config = self._resolve_environment_variables(merged_config)
            
            # 6. 验证配置
            if validate_schema:
                validation_result = self._validate_config(config_name, merged_config)
                if not validation_result.is_valid:
                    raise ValueError(f"配置验证失败: {validation_result.errors}")
                
                if validation_result.warnings:
                    for warning in validation_result.warnings:
                        logger.warning(f"⚠️ 配置警告: {warning}")
            
            # 7. 缓存配置
            if use_cache:
                self._config_cache[cache_key] = merged_config
                self._update_file_timestamps(config_name, environment)
            
            logger.info(f"✅ 配置加载完成: {config_name}")
            return merged_config
            
        except Exception as e:
            logger.error(f"❌ 配置加载失败: {config_name}: {e}")
            raise
    
    def _load_base_config(self, config_name: str) -> Dict[str, Any]:
        """加载基础配置文件"""
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            logger.warning(f"基础配置文件不存在: {config_file}")
            return {}
        
        return self._load_yaml_file(config_file)
    
    def _load_environment_config(self, config_name: str, environment: str) -> Dict[str, Any]:
        """加载环境特定配置文件"""
        env_config_file = self.config_dir / f"{config_name}.{environment}.yaml"
        
        if not env_config_file.exists():
            logger.debug(f"环境配置文件不存在: {env_config_file}")
            return {}
        
        return self._load_yaml_file(env_config_file)
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载YAML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.load(f, Loader=EnvironmentVariableLoader) or {}
        except Exception as e:
            logger.error(f"❌ YAML文件加载失败: {file_path}: {e}")
            raise
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并配置"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _resolve_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """递归解析环境变量"""
        if isinstance(config, dict):
            return {k: self._resolve_environment_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_environment_variables(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            # 处理 ${VAR_NAME} 或 ${VAR_NAME:default} 格式
            var_expr = config[2:-1]  # 移除 ${ 和 }
            if ':' in var_expr:
                var_name, default_value = var_expr.split(':', 1)
                return os.getenv(var_name, default_value)
            else:
                env_value = os.getenv(var_expr)
                if env_value is None:
                    logger.warning(f"⚠️ 环境变量未设置: {var_expr}")
                    return config  # 返回原始字符串
                return env_value
        else:
            return config
    
    def _validate_config(self, config_name: str, config: Dict[str, Any]) -> ConfigValidationResult:
        """验证配置"""
        schema_file = self.schema_dir / f"{config_name}.schema.yaml"
        
        if not schema_file.exists():
            logger.debug(f"配置schema不存在: {schema_file}")
            return ConfigValidationResult(is_valid=True)
        
        try:
            # 加载schema
            schema = self._load_schema(config_name)
            
            # 验证配置
            validate(instance=config, schema=schema)
            
            return ConfigValidationResult(is_valid=True)
            
        except ValidationError as e:
            return ConfigValidationResult(
                is_valid=False,
                errors=[str(e)]
            )
        except Exception as e:
            logger.error(f"❌ 配置验证异常: {e}")
            return ConfigValidationResult(
                is_valid=False,
                errors=[f"验证异常: {str(e)}"]
            )
    
    def _load_schema(self, config_name: str) -> Dict[str, Any]:
        """加载配置schema"""
        if config_name in self._schema_cache:
            return self._schema_cache[config_name]
        
        schema_file = self.schema_dir / f"{config_name}.schema.yaml"
        schema = self._load_yaml_file(schema_file)
        
        self._schema_cache[config_name] = schema
        return schema
    
    def _is_config_changed(self, config_name: str, environment: str) -> bool:
        """检查配置文件是否已更改"""
        files_to_check = [
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / f"{config_name}.{environment}.yaml"
        ]
        
        for file_path in files_to_check:
            if file_path.exists():
                current_timestamp = file_path.stat().st_mtime
                cached_timestamp = self._file_timestamps.get(str(file_path), 0)
                
                if current_timestamp > cached_timestamp:
                    return True
        
        return False
    
    def _update_file_timestamps(self, config_name: str, environment: str):
        """更新文件时间戳缓存"""
        files_to_update = [
            self.config_dir / f"{config_name}.yaml",
            self.config_dir / f"{config_name}.{environment}.yaml"
        ]
        
        for file_path in files_to_update:
            if file_path.exists():
                self._file_timestamps[str(file_path)] = file_path.stat().st_mtime
    
    def save_config(self, 
                    config_name: str, 
                    config: Dict[str, Any],
                    environment: str = "development") -> bool:
        """保存配置到文件"""
        try:
            if environment == "development":
                config_file = self.config_dir / f"{config_name}.yaml"
            else:
                config_file = self.config_dir / f"{config_name}.{environment}.yaml"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            # 清除缓存
            cache_key = f"{config_name}_{environment}"
            if cache_key in self._config_cache:
                del self._config_cache[cache_key]
            
            logger.info(f"✅ 配置保存成功: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 配置保存失败: {e}")
            return False
    
    def create_from_template(self, 
                           template_name: str, 
                           config_name: str,
                           variables: Dict[str, Any] = None) -> bool:
        """从模板创建配置"""
        template_file = self.template_dir / f"{template_name}.template.yaml"
        
        if not template_file.exists():
            logger.error(f"模板文件不存在: {template_file}")
            return False
        
        try:
            # 加载模板
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 替换变量
            if variables:
                for key, value in variables.items():
                    template_content = template_content.replace(f"{{{key}}}", str(value))
            
            # 解析YAML
            config = yaml.safe_load(template_content)
            
            # 保存配置
            return self.save_config(config_name, config)
            
        except Exception as e:
            logger.error(f"❌ 从模板创建配置失败: {e}")
            return False
    
    def list_configs(self) -> List[str]:
        """列出所有配置文件"""
        configs = set()
        
        for file_path in self.config_dir.glob("*.yaml"):
            name = file_path.stem
            # 排除环境特定配置
            if '.' not in name:
                configs.add(name)
        
        return sorted(list(configs))
    
    def list_environments(self, config_name: str) -> List[str]:
        """列出配置的所有环境"""
        environments = set()
        
        pattern = f"{config_name}.*.yaml"
        for file_path in self.config_dir.glob(pattern):
            parts = file_path.stem.split('.')
            if len(parts) >= 2:
                env_name = '.'.join(parts[1:])  # 支持多级环境名
                environments.add(env_name)
        
        return sorted(list(environments))
    
    def reload_config(self, config_name: str, environment: str = "development") -> Dict[str, Any]:
        """重新加载配置（清除缓存）"""
        cache_key = f"{config_name}_{environment}"
        
        # 清除缓存
        if cache_key in self._config_cache:
            del self._config_cache[cache_key]
        
        # 清除文件时间戳
        files_to_clear = [
            str(self.config_dir / f"{config_name}.yaml"),
            str(self.config_dir / f"{config_name}.{environment}.yaml")
        ]
        
        for file_key in files_to_clear:
            if file_key in self._file_timestamps:
                del self._file_timestamps[file_key]
        
        logger.info(f"🔄 重新加载配置: {config_name} (环境: {environment})")
        return self.load_config(config_name, environment, use_cache=False)
    
    def get_config_metadata(self, config_name: str) -> Optional[ConfigMetadata]:
        """获取配置元数据"""
        try:
            config = self.load_config(config_name, validate_schema=False)
            metadata_dict = config.get('metadata', {})
            
            if not metadata_dict:
                return None
            
            return ConfigMetadata(
                name=metadata_dict.get('name', config_name),
                version=metadata_dict.get('version', '1.0.0'),
                description=metadata_dict.get('description', ''),
                author=metadata_dict.get('author', ''),
                created_at=datetime.fromisoformat(metadata_dict.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(metadata_dict.get('updated_at', datetime.now().isoformat())),
                schema_version=metadata_dict.get('schema_version', '1.0')
            )
            
        except Exception as e:
            logger.error(f"❌ 获取配置元数据失败: {e}")
            return None
    
    def clear_cache(self):
        """清除所有缓存"""
        self._config_cache.clear()
        self._schema_cache.clear()
        self._file_timestamps.clear()
        logger.info("🧹 配置缓存已清除")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            'config_cache_size': len(self._config_cache),
            'schema_cache_size': len(self._schema_cache),
            'file_timestamps_size': len(self._file_timestamps),
            'cached_configs': list(self._config_cache.keys())
        }


# 全局配置管理器实例
_config_manager_instance: Optional[YAMLConfigManager] = None


def get_config_manager(config_dir: str = "./config") -> YAMLConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager_instance
    
    if _config_manager_instance is None:
        _config_manager_instance = YAMLConfigManager(config_dir)
    
    return _config_manager_instance


def load_agent_config(agent_name: str, 
                     environment: str = None,
                     config_dir: str = "./config") -> Dict[str, Any]:
    """便利函数：加载Agent配置"""
    if environment is None:
        environment = os.getenv('ADC_ENVIRONMENT', 'development')
    
    config_manager = get_config_manager(config_dir)
    return config_manager.load_config(agent_name, environment) 
"""
UniversalContext单元测试
测试上下文抽象类的所有功能
"""

import pytest
from datetime import datetime
from layers.framework.abstractions.context import UniversalContext


class TestUniversalContext:
    """测试UniversalContext类"""
    
    def test_context_creation(self):
        """测试上下文创建"""
        context = UniversalContext()
        assert context.data == {}
        assert context.session_id is None
        assert context.user_id is None
        assert isinstance(context.timestamp, datetime)
    
    def test_context_with_data(self):
        """测试带数据的上下文创建"""
        data = {"key": "value", "number": 42}
        context = UniversalContext(data=data)
        assert context.data == data
        assert context.get("key") == "value"
        assert context.get("number") == 42
    
    def test_context_with_session(self):
        """测试带会话ID的上下文创建"""
        session_id = "test_session_123"
        context = UniversalContext(session_id=session_id)
        assert context.session_id == session_id
    
    def test_context_with_user(self):
        """测试带用户ID的上下文创建"""
        user_id = "test_user_456"
        context = UniversalContext(user_id=user_id)
        assert context.user_id == user_id
    
    def test_get_method(self):
        """测试get方法"""
        context = UniversalContext(data={"key": "value"})
        assert context.get("key") == "value"
        assert context.get("missing", "default") == "default"
        assert context.get("missing") is None
    
    def test_set_method(self):
        """测试set方法"""
        context = UniversalContext()
        context.set("new_key", "new_value")
        assert context.data["new_key"] == "new_value"
        assert context.get("new_key") == "new_value"
    
    def test_update_method(self):
        """测试update方法"""
        context = UniversalContext(data={"key1": "value1"})
        update_data = {"key2": "value2", "key3": "value3"}
        context.update(update_data)
        assert context.data["key1"] == "value1"
        assert context.data["key2"] == "value2"
        assert context.data["key3"] == "value3"
    
    def test_clear_method(self):
        """测试clear方法"""
        context = UniversalContext(data={"key1": "value1", "key2": "value2"})
        context.clear()
        assert context.data == {}
    
    def test_copy_method(self):
        """测试copy方法"""
        original_data = {"key": "value", "nested": {"inner": "data"}}
        original_context = UniversalContext(
            data=original_data,
            session_id="test_session",
            user_id="test_user"
        )
        
        copied_context = original_context.copy()
        
        # 验证副本不是原对象
        assert copied_context is not original_context
        
        # 验证数据被正确复制
        assert copied_context.data == original_data
        assert copied_context.session_id == original_context.session_id
        assert copied_context.user_id == original_context.user_id
        
        # 验证修改副本不影响原对象
        copied_context.set("new_key", "new_value")
        assert "new_key" in copied_context.data
        assert "new_key" not in original_context.data
        
        # 验证修改原对象不影响副本
        original_context.set("original_key", "original_value")
        assert "original_key" in original_context.data
        assert "original_key" not in copied_context.data
    
    def test_copy_with_nested_data(self):
        """测试复制包含嵌套数据的上下文"""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                }
            },
            "list_data": [1, 2, 3],
            "string_data": "test"
        }
        
        context = UniversalContext(data=nested_data)
        copied = context.copy()
        
        # 验证嵌套数据被正确复制
        assert copied.data["level1"]["level2"]["level3"] == "deep_value"
        assert copied.data["list_data"] == [1, 2, 3]
        assert copied.data["string_data"] == "test"
    
    def test_context_immutability_after_copy(self):
        """测试复制后原上下文的不可变性"""
        original = UniversalContext(data={"key": "value"})
        copied = original.copy()
        
        # 修改副本
        copied.set("new_key", "new_value")
        
        # 原上下文应该保持不变
        assert "new_key" not in original.data
        assert original.data == {"key": "value"}
    
    def test_context_with_complex_data_types(self):
        """测试包含复杂数据类型的上下文"""
        complex_data = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None
        }
        
        context = UniversalContext(data=complex_data)
        copied = context.copy()
        
        # 验证所有数据类型都被正确复制
        for key, value in complex_data.items():
            assert copied.get(key) == value
            assert type(copied.get(key)) == type(value)
    
    def test_context_timestamp_handling(self):
        """测试时间戳处理"""
        before_creation = datetime.now()
        context = UniversalContext()
        after_creation = datetime.now()
        
        # 验证时间戳在合理范围内
        assert before_creation <= context.timestamp <= after_creation
        
        # 复制后的时间戳应该相同
        copied = context.copy()
        assert copied.timestamp == context.timestamp 
# -*- coding: utf-8 -*-
import pytest
from unittest.mock import Mock, patch
from loguru import logger

from use_notify.loguru_integration import LoguruReporter, setup_loguru_reporter
from use_notify import useNotifyChannel, useNotify


class TestLoguruReporter:
    """LoguruReporter测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清理logger配置
        logger.remove()
        logger.add(lambda _: None)  # 添加一个空的handler避免输出
    
    def test_reporter_initialization(self):
        """测试上报器初始化"""
        # 测试默认初始化
        reporter = LoguruReporter()
        assert reporter.notify is not None
        assert not reporter._is_configured
        
        # 测试使用自定义notify实例初始化
        notify = useNotify()
        reporter = LoguruReporter(notify)
        assert reporter.notify is notify
    
    def test_add_channel(self):
        """测试添加通道"""
        reporter = LoguruReporter()
        
        # 创建mock通道
        mock_channel = Mock()
        reporter.add_channel(mock_channel)
        
        assert mock_channel in reporter.notify.channels
    
    def test_configure_logger(self):
        """测试配置logger"""
        reporter = LoguruReporter()
        
        # 配置logger
        reporter.configure_logger(level="ERROR")
        
        assert reporter._is_configured
        assert hasattr(logger, 'report')
        
        # 重复配置应该不会有问题
        reporter.configure_logger(level="INFO")
        assert reporter._is_configured
    
    @patch('use_notify.loguru_integration.sys.stderr')
    def test_report_handler(self, mock_stderr):
        """测试上报处理器"""
        # 创建mock notify
        mock_notify = Mock()
        reporter = LoguruReporter(mock_notify)
        
        # 创建mock message
        mock_record = {
            'time': Mock(),
            'level': Mock(name='ERROR'),
            'name': 'test_module',
            'function': 'test_function',
            'line': 123,
            'message': 'Test error message',
            'exception': None,
            'extra': {'report': True, 'report_info': {'key': 'value'}}
        }
        mock_record['time'].strftime.return_value = '2023-01-01 12:00:00'
        
        mock_message = Mock()
        mock_message.record = mock_record
        
        # 调用处理器
        reporter._report_handler(mock_message)
        
        # 验证notify.publish被调用
        mock_notify.publish.assert_called_once()
        args, kwargs = mock_notify.publish.call_args
        assert 'title' in kwargs
        assert 'content' in kwargs
        assert 'ERROR' in kwargs['title']
        assert 'Test error message' in kwargs['content']
    
    def test_report_method_creation(self):
        """测试report方法创建"""
        reporter = LoguruReporter()
        report_method = reporter._create_report_method()
        
        assert callable(report_method)
    
    def test_from_settings(self):
        """测试从配置创建实例"""
        settings = {
            "BARK": {"token": "test_token"},
        }
        
        with patch('use_notify.notification.Notify.from_settings') as mock_from_settings:
            mock_notify = Mock()
            mock_from_settings.return_value = mock_notify
            
            reporter = LoguruReporter.from_settings(settings)
            
            mock_from_settings.assert_called_once_with(settings)
            assert reporter.notify is mock_notify
            assert reporter._is_configured


class TestGlobalFunctions:
    """全局函数测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清理全局状态
        import use_notify.loguru_integration
        use_notify.loguru_integration._global_reporter = None
        
        # 清理logger配置
        logger.remove()
        logger.add(lambda _: None)
    
    def test_setup_loguru_reporter_with_settings(self):
        """测试使用配置设置全局上报器"""
        settings = {"BARK": {"token": "test_token"}}
        
        with patch('use_notify.loguru_integration.LoguruReporter.from_settings') as mock_from_settings:
            mock_reporter = Mock()
            mock_from_settings.return_value = mock_reporter
            
            result = setup_loguru_reporter(settings=settings)
            
            mock_from_settings.assert_called_once_with(settings, level="ERROR")
            assert result is mock_reporter
    
    def test_setup_loguru_reporter_with_channels(self):
        """测试使用通道设置全局上报器"""
        mock_channel = Mock()
        channels = [mock_channel]
        
        with patch('use_notify.loguru_integration.Notify') as mock_notify_class:
            with patch('use_notify.loguru_integration.LoguruReporter') as mock_reporter_class:
                mock_notify = Mock()
                mock_reporter = Mock()
                mock_notify_class.return_value = mock_notify
                mock_reporter_class.return_value = mock_reporter
                
                result = setup_loguru_reporter(channels=channels)
                
                mock_notify_class.assert_called_once_with(channels)
                mock_reporter_class.assert_called_once_with(mock_notify)
                mock_reporter.configure_logger.assert_called_once_with(level="ERROR")
                assert result is mock_reporter
    
    def test_setup_loguru_reporter_default(self):
        """测试默认设置全局上报器"""
        with patch('use_notify.loguru_integration.LoguruReporter') as mock_reporter_class:
            mock_reporter = Mock()
            mock_reporter_class.return_value = mock_reporter
            
            result = setup_loguru_reporter()
            
            mock_reporter_class.assert_called_once_with()
            mock_reporter.configure_logger.assert_called_once_with(level="ERROR")
            assert result is mock_reporter
    
    def test_get_reporter(self):
        """测试获取全局上报器"""
        from use_notify.loguru_integration import get_reporter
        
        # 初始状态应该返回None
        assert get_reporter() is None
        
        # 设置后应该返回实例
        settings = {"BARK": {"token": "test_token"}}
        with patch('use_notify.loguru_integration.LoguruReporter.from_settings') as mock_from_settings:
            mock_reporter = Mock()
            mock_from_settings.return_value = mock_reporter
            
            setup_loguru_reporter(settings=settings)
            assert get_reporter() is mock_reporter


if __name__ == "__main__":
    pytest.main([__file__])
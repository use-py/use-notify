#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实项目中的loguru日志上报使用示例

这个示例展示了在实际项目中如何使用loguru日志上报功能
包括Web应用、数据处理、定时任务等场景
"""

import os
import time
import random
from datetime import datetime
from loguru import logger
from use_notify import setup_loguru_reporter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from use_notify.loguru_types import ExtendedLogger
    logger = logger  # type: ExtendedLogger


# 模拟配置（实际项目中应该从环境变量或配置文件读取）
NOTIFY_SETTINGS = {
    "BARK": {"token": os.getenv("BARK_TOKEN", "your_bark_token")},
    "WECHAT": {"token": os.getenv("WECHAT_TOKEN", "your_wechat_token")},
}


def setup_logging():
    """设置日志配置"""
    # 移除默认handler
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG"
    )
    
    # 添加文件日志
    logger.add(
        "logs/app_{time}.log",
        rotation="1 day",
        retention="30 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # 设置日志上报（只有ERROR及以上级别才上报）
    setup_loguru_reporter(settings=NOTIFY_SETTINGS, level="ERROR")
    
    logger.info("日志系统初始化完成")


class DatabaseManager:
    """数据库管理器示例"""
    
    def __init__(self):
        self.connected = False
        self.retry_count = 0
        self.max_retries = 3
    
    def connect(self):
        """连接数据库"""
        try:
            # 模拟数据库连接
            if random.random() < 0.8:  # 80%成功率
                self.connected = True
                logger.info("数据库连接成功")
                return True
            else:
                raise ConnectionError("数据库连接失败")
                
        except Exception as e:
            self.retry_count += 1
            
            if self.retry_count >= self.max_retries:
                # 达到最大重试次数，上报错误
                logger.report(
                    f"数据库连接失败，已重试{self.max_retries}次",
                    level="CRITICAL",
                    错误信息=str(e),
                    重试次数=self.retry_count,
                    服务器=os.getenv("HOSTNAME", "unknown"),
                    时间戳=datetime.now().isoformat()
                )
                return False
            else:
                logger.warning(f"数据库连接失败，正在重试({self.retry_count}/{self.max_retries}): {e}")
                time.sleep(1)
                return self.connect()
    
    def execute_query(self, sql):
        """执行SQL查询"""
        if not self.connected:
            logger.error("数据库未连接")
            return None
        
        try:
            # 模拟SQL执行
            if "DROP" in sql.upper():
                raise ValueError("危险的SQL操作被阻止")
            
            if random.random() < 0.95:  # 95%成功率
                logger.debug(f"SQL执行成功: {sql[:50]}...")
                return {"status": "success", "rows": random.randint(1, 100)}
            else:
                raise RuntimeError("SQL执行超时")
                
        except Exception as e:
            # SQL执行失败，上报错误
            logger.report(
                f"SQL执行失败: {str(e)}",
                level="ERROR",
                SQL语句=sql,
                数据库状态="connected" if self.connected else "disconnected",
                执行时间=datetime.now().isoformat()
            )
            return None


class WebApplication:
    """Web应用示例"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.request_count = 0
        self.error_count = 0
    
    def handle_request(self, user_id, action):
        """处理用户请求"""
        self.request_count += 1
        
        try:
            logger.info(f"处理用户请求: user_id={user_id}, action={action}")
            
            # 模拟业务逻辑
            if action == "login":
                return self._handle_login(user_id)
            elif action == "purchase":
                return self._handle_purchase(user_id)
            elif action == "admin_delete":
                return self._handle_admin_action(user_id, action)
            else:
                logger.warning(f"未知的操作类型: {action}")
                return {"status": "error", "message": "未知操作"}
                
        except Exception as e:
            self.error_count += 1
            
            # 计算错误率
            error_rate = self.error_count / self.request_count
            
            if error_rate > 0.1:  # 错误率超过10%
                logger.report(
                    f"系统错误率过高: {error_rate:.2%}",
                    level="CRITICAL",
                    当前错误="{}".format(str(e)),
                    总请求数=self.request_count,
                    错误数量=self.error_count,
                    用户ID=user_id,
                    操作=action
                )
            else:
                logger.report(
                    f"用户请求处理失败: {str(e)}",
                    level="ERROR",
                    用户ID=user_id,
                    操作=action,
                    请求序号=self.request_count
                )
            
            return {"status": "error", "message": "服务器内部错误"}
    
    def _handle_login(self, user_id):
        """处理登录"""
        if random.random() < 0.9:  # 90%成功率
            logger.info(f"用户登录成功: {user_id}")
            return {"status": "success", "token": f"token_{user_id}_{int(time.time())}"}
        else:
            raise ValueError("用户名或密码错误")
    
    def _handle_purchase(self, user_id):
        """处理购买"""
        amount = random.randint(10, 1000)
        
        if amount > 500:  # 大额交易需要特别关注
            logger.report(
                f"检测到大额交易",
                level="WARNING",
                用户ID=user_id,
                交易金额=amount,
                交易时间=datetime.now().isoformat(),
                风险等级="高" if amount > 800 else "中"
            )
        
        if random.random() < 0.95:  # 95%成功率
            logger.info(f"交易成功: user_id={user_id}, amount={amount}")
            return {"status": "success", "amount": amount}
        else:
            raise RuntimeError("支付网关错误")
    
    def _handle_admin_action(self, user_id, action):
        """处理管理员操作"""
        # 管理员敏感操作需要上报
        logger.report(
            f"管理员执行敏感操作",
            level="WARNING",
            管理员ID=user_id,
            操作类型=action,
            执行时间=datetime.now().isoformat(),
            IP地址="192.168.1.100",  # 模拟IP
            操作风险="高"
        )
        
        if random.random() < 0.8:  # 80%成功率
            logger.info(f"管理员操作成功: {action}")
            return {"status": "success"}
        else:
            raise PermissionError("权限不足")


class DataProcessor:
    """数据处理器示例"""
    
    def process_batch(self, batch_id, data_size):
        """批量数据处理"""
        logger.info(f"开始处理批次: {batch_id}, 数据量: {data_size}")
        
        try:
            # 模拟数据处理
            processing_time = random.uniform(1, 5)
            time.sleep(processing_time)
            
            if random.random() < 0.9:  # 90%成功率
                logger.info(f"批次处理完成: {batch_id}, 耗时: {processing_time:.2f}s")
                
                # 处理时间过长需要关注
                if processing_time > 4:
                    logger.report(
                        f"数据处理耗时过长",
                        level="WARNING",
                        批次ID=batch_id,
                        数据量=data_size,
                        处理时间=f"{processing_time:.2f}s",
                        性能指标="异常"
                    )
                
                return {"status": "success", "processed": data_size}
            else:
                raise RuntimeError("数据处理失败")
                
        except Exception as e:
            logger.report(
                f"批量数据处理失败",
                level="ERROR",
                批次ID=batch_id,
                数据量=data_size,
                错误信息=str(e),
                失败时间=datetime.now().isoformat()
            )
            return {"status": "error"}


def simulate_system_monitoring():
    """模拟系统监控"""
    logger.info("开始系统监控")
    
    # 模拟系统指标
    cpu_usage = random.uniform(0.1, 0.95)
    memory_usage = random.uniform(0.2, 0.9)
    disk_usage = random.uniform(0.3, 0.95)
    
    # 检查系统资源使用情况
    if cpu_usage > 0.8:
        logger.report(
            f"CPU使用率过高: {cpu_usage:.2%}",
            level="WARNING",
            CPU使用率=f"{cpu_usage:.2%}",
            内存使用率=f"{memory_usage:.2%}",
            磁盘使用率=f"{disk_usage:.2%}",
            监控时间=datetime.now().isoformat()
        )
    
    if memory_usage > 0.85:
        logger.report(
            f"内存使用率过高: {memory_usage:.2%}",
            level="ERROR",
            内存使用率=f"{memory_usage:.2%}",
            建议操作="重启服务或清理缓存"
        )
    
    if disk_usage > 0.9:
        logger.report(
            f"磁盘空间不足: {disk_usage:.2%}",
            level="CRITICAL",
            磁盘使用率=f"{disk_usage:.2%}",
            剩余空间=f"{(1-disk_usage)*100:.1f}GB",
            紧急程度="高"
        )


def main():
    """主函数"""
    print("=== 真实项目loguru日志上报示例 ===")
    print("注意: 这是演示代码，请配置正确的通知token")
    
    # 设置日志
    setup_logging()
    
    # 创建应用实例
    app = WebApplication()
    processor = DataProcessor()
    
    # 模拟各种场景
    scenarios = [
        # Web请求处理
        lambda: app.handle_request("user_001", "login"),
        lambda: app.handle_request("user_002", "purchase"),
        lambda: app.handle_request("admin_001", "admin_delete"),
        lambda: app.handle_request("user_003", "unknown_action"),
        
        # 数据处理
        lambda: processor.process_batch("batch_001", 1000),
        lambda: processor.process_batch("batch_002", 5000),
        
        # 系统监控
        lambda: simulate_system_monitoring(),
        
        # 数据库操作
        lambda: app.db.connect(),
        lambda: app.db.execute_query("SELECT * FROM users"),
        lambda: app.db.execute_query("DROP TABLE users"),  # 危险操作
    ]
    
    # 执行场景
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- 场景 {i} ---")
        try:
            result = scenario()
            if result:
                logger.debug(f"场景执行结果: {result}")
        except Exception as e:
            logger.error(f"场景执行异常: {e}")
        
        time.sleep(0.5)  # 间隔执行
    
    print("\n=== 演示完成 ===")
    print("在实际项目中，这些上报消息将通过配置的通知渠道发送")


if __name__ == "__main__":
    main()
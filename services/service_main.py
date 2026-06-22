"""
FloatMask后台服务入口
职责：作为Android前台服务的Python脚本入口
作用：保持应用在后台运行，防止被系统杀死

注意：此文件由Buildozer配置为后台服务入口，
独立于主App运行，用于维持悬浮窗服务的生命周期
"""

import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """服务主函数"""
    logger.info("FloatMask后台服务启动")
    
    try:
        # 导入Android相关模块
        from jnius import autoclass
        
        # 获取Android类
        PythonService = autoclass('org.kivy.android.PythonService')
        Notification = autoclass('android.app.Notification')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationManager = autoclass('android.app.NotificationManager')
        Context = autoclass('android.content.Context')
        
        # 获取服务上下文
        context = PythonService.mService
        
        # 创建通知渠道（Android 8.0+）
        channel_id = 'floatmask_service'
        channel_name = 'FloatMask服务'
        importance = NotificationManager.IMPORTANCE_LOW
        
        channel = NotificationChannel(channel_id, channel_name, importance)
        channel.setDescription('FloatMask悬浮窗服务')
        channel.enableLights(False)
        channel.enableVibration(False)
        
        # 创建通知管理器
        notification_manager = context.getSystemService(Context.NOTIFICATION_SERVICE)
        notification_manager.createNotificationChannel(channel)
        
        # 创建通知
        notification = Notification.Builder(context, channel_id) \
            .setContentTitle('FloatMask 运行中') \
            .setContentText('悬浮窗已激活，点击打开设置') \
            .setSmallIcon(android.R.drawable.ic_menu_info_details) \
            .setOngoing(True) \
            .build()
        
        # 启动前台服务
        context.startForeground(1, notification)
        
        logger.info("FloatMask后台服务已启动")
        
        # 保持服务运行
        while True:
            # 这里可以添加服务保活逻辑
            import time
            time.sleep(60)
            
    except ImportError:
        logger.warning("非Android环境，后台服务已跳过")
    except Exception as e:
        logger.error(f"后台服务启动失败: {e}")


if __name__ == '__main__':
    main()

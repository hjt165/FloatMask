"""
服务保活模块
实现Android前台服务保活机制，防止系统自动关闭悬浮窗服务
"""

from kivy.utils import platform
from app.utils.logger import logger


class KeepAliveService:
    """
    服务保活服务
    通过前台服务通知、WakeLock等机制保持服务运行
    """

    def __init__(self):
        self.is_running = False
        self._wake_lock = None
        self._notification_id = 1001

    def start(self):
        if self.is_running:
            logger.warning('KeepAlive', '服务已在运行，跳过重复启动')
            return

        self.is_running = True

        if platform == 'android':
            self._start_foreground_service()
            self._acquire_wake_lock()

        logger.info('KeepAlive', '保活服务已启动')

    def stop(self):
        if not self.is_running:
            return

        self.is_running = False

        if platform == 'android':
            self._release_wake_lock()
            self._stop_foreground_service()

        logger.info('KeepAlive', '保活服务已停止')

    def _start_foreground_service(self):
        try:
            from jnius import autoclass

            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity

            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationChannel = autoclass('android.app.NotificationChannel')
            Builder = autoclass('android.app.Notification$Builder')

            channel_id = 'floatmask_service'
            channel_name = 'FloatMask悬浮框服务'

            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)

            if hasattr(nm, 'createNotificationChannel'):
                channel = NotificationChannel(
                    channel_id,
                    channel_name,
                    NotificationManager.IMPORTANCE_LOW
                )
                channel.setDescription('FloatMask悬浮窗后台服务')
                nm.createNotificationChannel(channel)

            R = autoclass('android.R')

            notification = Builder(activity, channel_id) \
                .setContentTitle('FloatMask') \
                .setContentText('悬浮框服务正在运行') \
                .setSmallIcon(R.drawable.ic_menu_info_details) \
                .setOngoing(True) \
                .build()

            activity.startForeground(self._notification_id, notification)

            logger.info('KeepAlive', '前台服务已启动')

        except Exception as e:
            logger.error('KeepAlive', f'启动前台服务失败: {e}')

    def _stop_foreground_service(self):
        try:
            from jnius import autoclass

            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity

            Build = autoclass('android.os.Build')
            if Build.VERSION.SDK_INT >= 24:
                activity.stopForeground(1)
            else:
                activity.stopForeground(True)

            logger.info('KeepAlive', '前台服务已停止')

        except Exception as e:
            logger.error('KeepAlive', f'停止前台服务失败: {e}')

    def _acquire_wake_lock(self):
        try:
            from jnius import autoclass

            PythonActivity = autoclass('org.renpy.android.PythonActivity')
            activity = PythonActivity.mActivity

            Context = autoclass('android.content.Context')
            PowerManager = autoclass('android.os.PowerManager')

            pm = activity.getSystemService(Context.POWER_SERVICE)
            self._wake_lock = pm.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "FloatMask:KeepAlive"
            )
            self._wake_lock.acquire()

            logger.info('KeepAlive', 'WakeLock已获取')

        except Exception as e:
            logger.error('KeepAlive', f'获取WakeLock失败: {e}')

    def _release_wake_lock(self):
        try:
            if self._wake_lock and self._wake_lock.isHeld():
                self._wake_lock.release()
                self._wake_lock = None
                logger.info('KeepAlive', 'WakeLock已释放')
        except Exception as e:
            logger.error('KeepAlive', f'释放WakeLock失败: {e}')

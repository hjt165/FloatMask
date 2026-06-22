"""
权限处理器模块
负责检测和请求Android悬浮窗权限(SYSTEM_ALERT_WINDOW)
"""

from kivy.utils import platform


class PermissionHandler:
    """悬浮窗权限处理器"""

    def __init__(self):
        """初始化权限处理器"""
        self.permission_granted = False

    def check_permission(self):
        """
        检测悬浮窗权限是否已授予

        Returns:
            bool: 权限是否已授予
        """
        if platform == 'android':
            return self._check_android_permission()
        else:
            # 非Android平台默认返回True（用于PC测试）
            return True

    def request_permission(self):
        """
        请求悬浮窗权限
        如果权限未授予，跳转到系统设置页面
        """
        if platform == 'android':
            self._request_android_permission()

    def _check_android_permission(self):
        """
        检测Android悬浮窗权限

        Returns:
            bool: 权限是否已授予
        """
        try:
            from jnius import autoclass

            # 获取Android API类
            Settings = autoclass('android.provider.Settings')
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            # 获取当前Activity
            activity = PythonActivity.mActivity

            # 检测权限（Android 6.0+）
            if self._get_sdk_version() >= 23:
                self.permission_granted = Settings.canDrawOverlays(activity)
            else:
                # Android 6.0以下默认有权限
                self.permission_granted = True

            return self.permission_granted

        except Exception as e:
            print(f"权限检测失败: {e}")
            return False

    def _request_android_permission(self):
        """
        请求Android悬浮窗权限
        跳转到系统设置页面让用户手动开启
        """
        try:
            from jnius import autoclass

            # 获取Android API类
            Settings = autoclass('android.provider.Settings')
            Context = autoclass('android.content.Context')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            # 获取当前Activity
            activity = PythonActivity.mActivity
            package_name = activity.getPackageName()

            # 创建跳转到权限设置页面的Intent
            intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse(f"package:{package_name}")
            )

            # 启动设置页面
            activity.startActivity(intent)

            print(f"已跳转到悬浮窗权限设置页面: {package_name}")

        except Exception as e:
            print(f"请求权限失败: {e}")

    def _get_sdk_version(self):
        """
        获取Android SDK版本号

        Returns:
            int: SDK版本号
        """
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            sdk = Build.VERSION.SDK_INT
            if sdk and int(sdk) > 0:
                return int(sdk)
        except Exception:
            pass
        # Fallback
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            return int(activity.getApplicationInfo().targetSdkVersion)
        except Exception:
            return 32

    def get_permission_status_text(self):
        """
        获取权限状态文本

        Returns:
            str: 权限状态描述
        """
        if self.check_permission():
            return "悬浮窗权限: 已授权"
        else:
            return "悬浮窗权限: 未授权（点击下方按钮开启）"

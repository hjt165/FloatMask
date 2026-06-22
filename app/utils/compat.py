"""
兼容性处理模块
适配不同Android版本和厂商（华为、小米、OPPO、vivo等）的差异
"""

from kivy.utils import platform
from app.utils.logger import logger


class CompatManager:
    """
    兼容性管理器
    检测Android版本、厂商信息，提供兼容性处理
    """

    def __init__(self):
        self._sdk_version = None
        self._manufacturer = None
        self._model = None
        self._brand = None

    @property
    def sdk_version(self):
        if self._sdk_version is None:
            self._sdk_version = self._get_sdk_version()
        return self._sdk_version

    @property
    def manufacturer(self):
        if self._manufacturer is None:
            self._manufacturer = self._get_property('MANUFACTURER')
        return self._manufacturer

    @property
    def model(self):
        if self._model is None:
            self._model = self._get_property('MODEL')
        return self._model

    @property
    def brand(self):
        if self._brand is None:
            self._brand = self._get_property('BRAND')
        return self._brand

    def _get_sdk_version(self):
        if platform != 'android':
            return 33
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            sdk = Build.VERSION.SDK_INT
            if sdk and int(sdk) > 0:
                return int(sdk)
        except Exception:
            pass
        # Fallback: read system property
        try:
            from jnius import autoclass
            System = autoclass('java.lang.System')
            val = System.getProperty("android.os.Build.VERSION.SDK_INT")
            if val:
                return int(val)
        except Exception:
            pass
        # Fallback: read from Activity's targetSdkVersion
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            return int(activity.getApplicationInfo().targetSdkVersion)
        except Exception:
            return 32

    def _get_property(self, prop_name):
        if platform != 'android':
            return 'unknown'
        try:
            from jnius import autoclass
            Build = autoclass('android.os.Build')
            return getattr(Build, prop_name, 'unknown')
        except Exception:
            return 'unknown'

    def is_huawei(self):
        return self.manufacturer.lower() in ('huawei', 'honor')

    def is_xiaomi(self):
        return self.manufacturer.lower() in ('xiaomi', 'redmi')

    def is_oppo(self):
        return self.manufacturer.lower() in ('oppo', 'oneplus', 'realme')

    def is_vivo(self):
        return self.manufacturer.lower() in ('vivo', 'iqoo')

    def is_samsung(self):
        return self.manufacturer.lower() == 'samsung'

    def is_meizu(self):
        return self.manufacturer.lower() == 'meizu'

    def get_overlay_permission_method(self):
        if platform != 'android':
            return 'standard'

        if self.sdk_version < 23:
            return 'auto_grant'

        if self.is_xiaomi():
            return 'xiaomi_special'
        elif self.is_huawei():
            return 'huawei_special'
        elif self.is_oppo():
            return 'oppo_special'
        elif self.is_vivo():
            return 'vivo_special'
        elif self.is_samsung():
            return 'samsung_special'
        elif self.is_meizu():
            return 'meizu_special'
        else:
            return 'standard'

    def get_service_start_method(self):
        if platform != 'android':
            return 'normal'

        if self.sdk_version >= 26:
            return 'foreground_service'
        else:
            return 'normal'

    def should_use_foreground_service(self):
        return self.sdk_version >= 26

    def get_device_info(self):
        return {
            'sdk_version': self.sdk_version,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'brand': self.brand,
            'is_huawei': self.is_huawei(),
            'is_xiaomi': self.is_xiaomi(),
            'is_oppo': self.is_oppo(),
            'is_vivo': self.is_vivo(),
            'is_samsung': self.is_samsung(),
            'permission_method': self.get_overlay_permission_method(),
            'service_method': self.get_service_start_method(),
        }

    def print_device_info(self):
        info = self.get_device_info()
        logger.info('Compat', '=== Device Info ===')
        for key, value in info.items():
            logger.info('Compat', f'  {key}: {value}')
        logger.info('Compat', '==================')


compat = CompatManager()

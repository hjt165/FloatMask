"""
Android原生窗口模块
使用Android WindowManager API实现真正的跨App悬浮窗覆盖
支持TYPE_APPLICATION_OVERLAY、点击穿透、手势交互（拖拽/双击/长按/缩放）
"""

from kivy.utils import platform
from app.utils.logger import logger

GRAVITY_TOP_LEFT = 0x33
MIN_OVERLAY_SIZE = 80
COLORS_ARGB = [
    (204, 0, 0, 0),       # 纯黑半透明
    (204, 27, 94, 32),    # 深绿
    (204, 13, 71, 161),   # 深蓝
    (204, 183, 28, 28),   # 深红
    (204, 74, 20, 140),   # 深紫
    (204, 230, 81, 0),    # 深橙
]


class AndroidWindowManager:
    """
    Android WindowManager封装
    通过Pyjnius调用Android原生API管理悬浮窗
    """

    def __init__(self):
        self._window_manager = None
        self._view = None
        self._params = None
        self._is_showing = False
        self._touch_handler = None
        self._quick_menu_view = None
        self._quick_menu_params = None

    def check_permission(self):
        if platform != 'android':
            return True

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            Settings = autoclass('android.provider.Settings')
            return Settings.canDrawOverlays(activity)
        except Exception as e:
            logger.error('AndroidWindow', f'检查悬浮窗权限失败: {e}')
            return False

    def initialize(self):
        if platform != 'android':
            return False

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            Context = autoclass('android.content.Context')
            self._window_manager = activity.getSystemService(Context.WINDOW_SERVICE)

            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            self._params = LayoutParams()
            self._params.width = LayoutParams.WRAP_CONTENT
            self._params.height = LayoutParams.WRAP_CONTENT
            self._params.type = LayoutParams.TYPE_APPLICATION_OVERLAY
            self._params.flags = LayoutParams.FLAG_NOT_FOCUSABLE
            self._params.gravity = GRAVITY_TOP_LEFT
            self._params.x = 100
            self._params.y = 100

            self._load_jar()
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'初始化失败: {e}')
            return False

    def _load_jar(self):
        """加载预编译的触摸处理Java类"""
        if platform != 'android':
            return

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            context = activity.getApplicationContext()
            asset_manager = context.getAssets()

            import os
            jar_name = 'libs/overlay-touch-handler.jar'
            jar_path = os.path.join(activity.getFilesDir().getAbsolutePath(), jar_name)

            os.makedirs(os.path.dirname(jar_path), exist_ok=True)

            if not os.path.exists(jar_path):
                try:
                    from jnius import autoclass
                    PythonActivity = autoclass('org.kivy.android.PythonActivity')
                    activity = PythonActivity.mActivity
                    asset_manager = activity.getAssets()

                    input_stream = asset_manager.open(jar_name)
                    fileOutputStream = autoclass('java.io.FileOutputStream')(jar_path)
                    buffer = bytearray(4096)
                    while True:
                        bytes_read = input_stream.read(buffer)
                        if bytes_read == -1:
                            break
                        fileOutputStream.write(buffer[:bytes_read])
                    input_stream.close()
                    fileOutputStream.close()
                except Exception as e:
                    logger.warning('AndroidWindow', f'从assets复制JAR失败: {e}')

            if os.path.exists(jar_path):
                URLClassLoader = autoclass('java.net.URLClassLoader')
                File = autoclass('java.io.File')
                jar_file = File(jar_path)
                url = jar_file.toURI().toURL()
                class_loader = URLClassLoader([url], context.getClassLoader())

                JavaClass = autoclass('java.lang.Class')
                handler_class = JavaClass.forName(
                    'com.floatmask.overlay.OverlayTouchHandler',
                    True,
                    class_loader
                )
                self._touch_handler_class = handler_class
                logger.info('AndroidWindow', '触摸处理JAR加载成功')
        except Exception as e:
            logger.warning('AndroidWindow', f'加载触摸处理JAR失败: {e}')
            self._touch_handler_class = None

    def _create_overlay_view(self, width, height, color_index=0):
        """创建带样式的覆盖层视图（使用GradientDrawable）"""
        if platform != 'android':
            return None

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            LinearLayout = autoclass('android.widget.LinearLayout')
            TextView = autoclass('android.widget.TextView')
            GradientDrawable = autoclass('android.graphics.drawable.GradientDrawable')
            Color = autoclass('android.graphics.Color')
            Gravity = autoclass('android.view.Gravity')
            View = autoclass('android.view.View')

            container = LinearLayout(activity)
            container.setOrientation(LinearLayout.VERTICAL)

            r, g, b, a = COLORS_ARGB[color_index % len(COLORS_ARGB)]
            bg = GradientDrawable()
            bg.setColor(Color.argb(a, r, g, b))
            bg.setCornerRadius(20)
            bg.setStroke(3, Color.parseColor('#FF6B35'))
            container.setBackground(bg)
            container.setPadding(20, 15, 20, 15)

            label = TextView(activity)
            label.setText('FloatMask')
            label.setTextColor(Color.WHITE)
            label.setTextSize(13)
            container.addView(label)

            info = TextView(activity)
            info.setText('拖动: 移动\n双击: 切换颜色\n长按: 打开菜单')
            info.setTextColor(Color.parseColor('#BBBBBB'))
            info.setTextSize(10)
            info.setPadding(0, 5, 0, 0)
            container.addView(info)

            sep = View(activity)
            sep_layout_params = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 2
            )
            sep.setLayoutParams(sep_layout_params)
            sep_bg = GradientDrawable()
            sep_bg.setColor(Color.parseColor('#FF6B35'))
            sep.setBackground(sep_bg)
            container.addView(sep)

            return container
        except Exception as e:
            logger.error('AndroidWindow', f'创建覆盖层视图失败: {e}')
            return None

    def add_overlay_view(self, x, y, width, height, touch_through=False, color_index=0):
        if platform != 'android' or not self._window_manager:
            return False

        try:
            from jnius import autoclass
            PixelFormat = autoclass('android.view.PixelFormat')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')

            view = self._create_overlay_view(width, height, color_index)
            if not view:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                View = autoclass('android.view.View')
                Color = autoclass('android.graphics.Color')
                view = View(activity)
                view.setBackgroundColor(Color.argb(128, 128, 128, 128))

            self._params = LayoutParams(
                int(width),
                int(height),
                LayoutParams.TYPE_APPLICATION_OVERLAY,
                self._get_flags(touch_through),
                PixelFormat.TRANSLUCENT
            )
            self._params.x = int(x)
            self._params.y = int(y)
            self._params.gravity = GRAVITY_TOP_LEFT

            self._window_manager.addView(view, self._params)
            self._view = view
            self._is_showing = True

            if not touch_through:
                self._setup_touch_handler()

            return True
        except Exception as e:
            logger.error('AndroidWindow', f'添加悬浮视图失败: {e}')
            return False

    def _setup_touch_handler(self):
        """设置Java触摸处理器"""
        if platform != 'android' or not self._view or not self._params:
            return

        if not hasattr(self, '_touch_handler_class') or not self._touch_handler_class:
            logger.warning('AndroidWindow', '触摸处理类未加载，跳过手势设置')
            return

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            DisplayMetrics = autoclass('android.util.DisplayMetrics')
            dm = DisplayMetrics()
            activity.getWindowManager().getDefaultDisplay().getMetrics(dm)
            screen_width = dm.widthPixels
            screen_height = dm.heightPixels

            handler_instance = self._touch_handler_class(
                self._window_manager,
                self._params,
                self._view,
                screen_width,
                screen_height
            )

            OnTouchListener = autoclass('android.view.View$OnTouchListener')
            touch_listener = handler_instance.cast(OnTouchListener)
            self._view.setOnTouchListener(touch_listener)
            self._touch_handler = handler_instance

            logger.info('AndroidWindow', '触摸处理器设置成功')
        except Exception as e:
            logger.warning('AndroidWindow', f'设置触摸处理器失败: {e}')

    def remove_overlay_view(self):
        self._close_quick_menu()
        if platform != 'android' or not self._window_manager or not self._view:
            return False

        try:
            self._window_manager.removeView(self._view)
            self._view = None
            self._touch_handler = None
            self._is_showing = False
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'移除悬浮视图失败: {e}')
            return False

    def update_position(self, x, y):
        if not self._view or not self._params:
            return False

        try:
            self._params.x = int(x)
            self._params.y = int(y)
            self._window_manager.updateViewLayout(self._view, self._params)
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'更新位置失败: {e}')
            return False

    def update_size(self, width, height):
        if not self._view or not self._params:
            return False

        try:
            self._params.width = int(width)
            self._params.height = int(height)
            self._window_manager.updateViewLayout(self._view, self._params)
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'更新尺寸失败: {e}')
            return False

    def set_touch_through(self, enabled):
        if not self._view or not self._params:
            return False

        try:
            self._params.flags = self._get_flags(enabled)
            self._window_manager.updateViewLayout(self._view, self._params)

            if not enabled:
                self._setup_touch_handler()
            else:
                self._view.setOnTouchListener(None)

            return True
        except Exception as e:
            logger.error('AndroidWindow', f'设置点击穿透失败: {e}')
            return False

    def update_color(self, color_index):
        """更新覆盖层颜色"""
        if platform != 'android' or not self._view:
            return False

        try:
            from jnius import autoclass
            GradientDrawable = autoclass('android.graphics.drawable.GradientDrawable')
            Color = autoclass('android.graphics.Color')

            r, g, b, a = COLORS_ARGB[color_index % len(COLORS_ARGB)]
            bg = GradientDrawable()
            bg.setColor(Color.argb(a, r, g, b))
            bg.setCornerRadius(20)
            bg.setStroke(3, Color.parseColor('#FF6B35'))
            self._view.setBackground(bg)

            if self._touch_handler:
                self._touch_handler.setColorIndex(color_index)

            return True
        except Exception as e:
            logger.error('AndroidWindow', f'更新颜色失败: {e}')
            return False

    def minimize(self):
        """最小化悬浮窗（隐藏但保留触摸区域）"""
        if platform != 'android' or not self._view:
            return False

        try:
            self._view.setVisibility(4)  # View.INVISIBLE = 4
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'最小化失败: {e}')
            return False

    def restore(self):
        """恢复悬浮窗"""
        if platform != 'android' or not self._view:
            return False

        try:
            self._view.setVisibility(0)  # View.VISIBLE = 0
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'恢复失败: {e}')
            return False

    def show_quick_menu(self):
        """显示原生快捷菜单"""
        if platform != 'android' or not self._window_manager or not self._params:
            return False

        self._close_quick_menu()

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            LinearLayout = autoclass('android.widget.LinearLayout')
            TextView = autoclass('android.widget.TextView')
            GradientDrawable = autoclass('android.graphics.drawable.GradientDrawable')
            Color = autoclass('android.graphics.Color')
            Gravity = autoclass('android.view.Gravity')
            View = autoclass('android.view.View')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            PixelFormat = autoclass('android.view.PixelFormat')

            menu = LinearLayout(activity)
            menu.setOrientation(LinearLayout.VERTICAL)

            menu_bg = GradientDrawable()
            menu_bg.setColor(Color.parseColor('#F5F5F5'))
            menu_bg.setCornerRadius(16)
            menu_bg.setStroke(2, Color.parseColor('#FF6B35'))
            menu.setBackground(menu_bg)
            menu.setPadding(16, 12, 16, 12)

            title = TextView(activity)
            title.setText('快捷菜单')
            title.setTextSize(14)
            title.setTextColor(Color.BLACK)
            title.setPadding(0, 0, 0, 8)
            menu.addView(title)

            sep = View(activity)
            sep.setLayoutParams(LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1
            ))
            sep_bg = GradientDrawable()
            sep_bg.setColor(Color.parseColor('#E0E0E0'))
            sep.setBackground(sep_bg)
            menu.addView(sep)

            menuClickListener = self._create_menu_click_listener()

            items = [
                ('切换颜色', 0),
                ('透明度: 50%', 1),
                ('透明度: 100%', 2),
                ('关闭', 3),
            ]
            for text, action_id in items:
                item = TextView(activity)
                item.setText(text)
                item.setTextSize(13)
                item.setTextColor(Color.parseColor('#333333'))
                item.setPadding(12, 10, 12, 10)
                item.setTag(action_id)
                item.setOnClickListener(menuClickListener)
                menu.addView(item)

                item_sep = View(activity)
                item_sep.setLayoutParams(LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT, 1
                ))
                item_sep_bg = GradientDrawable()
                item_sep_bg.setColor(Color.parseColor('#EEEEEE'))
                item_sep.setBackground(item_sep_bg)
                menu.addView(item_sep)

            DisplayMetrics = autoclass('android.util.DisplayMetrics')
            dm = DisplayMetrics()
            activity.getWindowManager().getDefaultDisplay().getMetrics(dm)
            screen_w = dm.widthPixels
            screen_h = dm.heightPixels

            menu_params = LayoutParams(
                300,
                LayoutParams.WRAP_CONTENT,
                LayoutParams.TYPE_APPLICATION_OVERLAY,
                LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT
            )
            menu_params.gravity = Gravity.TOP | Gravity.START
            menu_params.x = min(self._params.x + 50, screen_w - 320)
            menu_params.y = self._params.y + self._params.height + 10
            if menu_params.y + 500 > screen_h:
                menu_params.y = max(0, self._params.y - 400)

            self._quick_menu_view = menu
            self._quick_menu_params = menu_params
            self._window_manager.addView(menu, menu_params)
            return True
        except Exception as e:
            logger.error('AndroidWindow', f'显示快捷菜单失败: {e}')
            return False

    def _create_menu_click_listener(self):
        """创建菜单项点击监听器（单个监听器通过tag区分菜单项）"""
        if platform != 'android':
            return None

        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity

            outer = self

            class MenuClickListenerImpl:
                def onClick(self, v):
                    action_id = v.getTag()
                    outer._on_menu_click(int(action_id))

            listener = MenuClickListenerImpl()
            return listener
        except Exception as e:
            logger.error('AndroidWindow', f'创建菜单监听器失败: {e}')
            return None

    def _on_menu_click(self, action_id):
        """处理菜单项点击"""
        self._close_quick_menu()

        if action_id == 0:
            if self._touch_handler:
                idx = (self._touch_handler.getColorIndex() + 1) % len(COLORS_ARGB)
                self.update_color(idx)
        elif action_id == 1:
            self._set_overlay_alpha(0.5)
        elif action_id == 2:
            self._set_overlay_alpha(1.0)
        elif action_id == 3:
            self.remove_overlay_view()

    def _set_overlay_alpha(self, alpha):
        """设置覆盖层透明度"""
        if platform != 'android' or not self._view:
            return

        try:
            self._view.setAlpha(alpha)
        except Exception as e:
            logger.error('AndroidWindow', f'设置透明度失败: {e}')

    def _close_quick_menu(self):
        """关闭快捷菜单"""
        if platform != 'android' or not self._quick_menu_view:
            return

        try:
            self._window_manager.removeView(self._quick_menu_view)
            self._quick_menu_view = None
            self._quick_menu_params = None
        except Exception:
            pass

    def _get_flags(self, touch_through):
        from jnius import autoclass
        LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
        flags = LayoutParams.FLAG_NOT_FOCUSABLE
        if touch_through:
            flags |= LayoutParams.FLAG_NOT_TOUCHABLE
        return flags

    @property
    def is_showing(self):
        return self._is_showing


class NativeOverlay:
    """
    原生悬浮窗封装
    提供简洁的API来管理Android原生悬浮窗
    """

    def __init__(self):
        self.manager = AndroidWindowManager()
        self._initialized = False
        self._color_index = 0

    def initialize(self):
        if self.manager.initialize():
            self._initialized = True
            return True
        return False

    def show(self, x=100, y=100, width=200, height=120, touch_through=False, color_index=0):
        if not self._initialized:
            if not self.initialize():
                return False

        self._color_index = color_index
        return self.manager.add_overlay_view(x, y, width, height, touch_through, color_index)

    def hide(self):
        return self.manager.remove_overlay_view()

    def move(self, x, y):
        return self.manager.update_position(x, y)

    def resize(self, width, height):
        return self.manager.update_size(width, height)

    def set_passthrough(self, enabled):
        return self.manager.set_touch_through(enabled)

    def set_color(self, color_index):
        self._color_index = color_index
        return self.manager.update_color(color_index)

    def minimize(self):
        return self.manager.minimize()

    def restore(self):
        return self.manager.restore()

    def show_menu(self):
        return self.manager.show_quick_menu()

    @property
    def is_visible(self):
        return self.manager.is_showing

    @property
    def color_index(self):
        return self._color_index

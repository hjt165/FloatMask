package com.floatmask.test;

import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.provider.Settings;
import android.util.Log;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final String TAG = "FloatMask";
    private static final int REQUEST_OVERLAY = 1001;
    private static final int MIN_SIZE = 200;
    private static final long DOUBLE_TAP_TIMEOUT = 300;
    private static final long LONG_PRESS_TIMEOUT = 500;

    private WindowManager windowManager;
    private View overlayView;
    private LinearLayout quickMenuView;
    private TextView statusText;
    private WindowManager.LayoutParams overlayParams;
    private boolean isOverlayShowing = false;
    private boolean isClickThrough = false;
    private boolean isMinimized = false;

    private final int[] overlayColors = {
        Color.parseColor("#CC000000"),
        Color.parseColor("#CC1B5E20"),
        Color.parseColor("#CC0D47A1"),
        Color.parseColor("#CCB71C1C"),
        Color.parseColor("#CC4A148C"),
        Color.parseColor("#CCE65100"),
    };
    private int currentColorIndex = 0;

    private float lastTouchX, lastTouchY;
    private int lastViewX, lastViewY;
    private boolean isDragging = false;
    private boolean isResizing = false;
    private float initialDistance;
    private int initialWidth, initialHeight;
    private long lastTapTime = 0;
    private long touchDownTime = 0;
    private float touchDownX, touchDownY;
    private int screenWidth, screenHeight;

    private final Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);

        android.util.DisplayMetrics dm = new android.util.DisplayMetrics();
        getWindowManager().getDefaultDisplay().getMetrics(dm);
        screenWidth = dm.widthPixels;
        screenHeight = dm.heightPixels;

        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        layout.setPadding(40, 40, 40, 40);
        layout.setBackgroundColor(Color.WHITE);

        TextView title = new TextView(this);
        title.setText("FloatMask - 安卓版");
        title.setTextSize(22);
        title.setTextColor(Color.BLACK);
        title.setGravity(Gravity.CENTER);
        layout.addView(title);

        statusText = new TextView(this);
        statusText.setText("就绪");
        statusText.setTextSize(14);
        statusText.setPadding(0, 20, 0, 0);
        statusText.setTextColor(Color.DKGRAY);
        statusText.setGravity(Gravity.CENTER);
        layout.addView(statusText);

        addSeparator(layout);

        TextView sectionLabel = new TextView(this);
        sectionLabel.setText("普通悬浮窗");
        sectionLabel.setTextSize(14);
        sectionLabel.setTextColor(Color.GRAY);
        sectionLabel.setPadding(0, 10, 0, 5);
        layout.addView(sectionLabel);

        Button showBtn = createButton("显示悬浮窗", v -> {
            if (!Settings.canDrawOverlays(MainActivity.this)) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()));
                startActivityForResult(intent, REQUEST_OVERLAY);
            } else {
                showNormalOverlay();
            }
        });
        layout.addView(showBtn);

        Button hideBtn = createButton("隐藏悬浮窗", v -> hideOverlay());
        layout.addView(hideBtn);

        addSeparator(layout);

        TextView clickThroughLabel = new TextView(this);
        clickThroughLabel.setText("点击穿透模式");
        clickThroughLabel.setTextSize(14);
        clickThroughLabel.setTextColor(Color.GRAY);
        clickThroughLabel.setPadding(0, 10, 0, 5);
        layout.addView(clickThroughLabel);

        Button clickThroughBtn = createButton("显示点击穿透窗", v -> {
            if (!Settings.canDrawOverlays(MainActivity.this)) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()));
                startActivityForResult(intent, REQUEST_OVERLAY);
            } else {
                showClickThroughOverlay();
            }
        });
        layout.addView(clickThroughBtn);

        addSeparator(layout);

        Button minimizeBtn = createButton("最小化悬浮窗", v -> {
            if (overlayView != null && isOverlayShowing) {
                overlayView.setVisibility(View.INVISIBLE);
                isMinimized = true;
                statusText.setText("悬浮窗已最小化");
            }
        });
        layout.addView(minimizeBtn);

        Button restoreBtn = createButton("恢复悬浮窗", v -> {
            if (overlayView != null && isOverlayShowing && isMinimized) {
                overlayView.setVisibility(View.VISIBLE);
                isMinimized = false;
                statusText.setText("悬浮窗已恢复");
            }
        });
        layout.addView(restoreBtn);

        setContentView(layout);
    }

    private void addSeparator(LinearLayout layout) {
        View sep = new View(this);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1);
        params.setMargins(0, 10, 0, 10);
        sep.setLayoutParams(params);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#E0E0E0"));
        sep.setBackground(bg);
        layout.addView(sep);
    }

    private Button createButton(String text, View.OnClickListener listener) {
        Button btn = new Button(this);
        btn.setText(text);
        btn.setTextSize(14);
        btn.setOnClickListener(listener);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        params.setMargins(0, 4, 0, 4);
        btn.setLayoutParams(params);
        return btn;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_OVERLAY) {
            if (Settings.canDrawOverlays(this)) {
                showNormalOverlay();
            } else {
                Toast.makeText(this, "权限被拒绝", Toast.LENGTH_SHORT).show();
            }
        }
    }

    private void showNormalOverlay() {
        if (isOverlayShowing) hideOverlay();
        isClickThrough = false;
        createAndShowOverlay(false);
    }

    private void showClickThroughOverlay() {
        if (isOverlayShowing) hideOverlay();
        isClickThrough = true;
        createAndShowOverlay(true);
    }

    private void createAndShowOverlay(boolean clickThrough) {
        overlayView = createOverlayContainer(clickThrough);

        overlayParams = new WindowManager.LayoutParams(
                clickThrough ? 400 : 400,
                clickThrough ? 200 : 600,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                clickThrough
                    ? WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                    : WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        overlayParams.gravity = Gravity.TOP | Gravity.START;
        overlayParams.x = 100;
        overlayParams.y = 100;

        overlayView.setTag(overlayParams);
        windowManager.addView(overlayView, overlayParams);
        isOverlayShowing = true;
        isMinimized = false;

        String mode = clickThrough ? "点击穿透" : "普通";
        statusText.setText(mode + "悬浮窗已显示");
        Log.i(TAG, mode + " overlay created: " + overlayParams.width + "x" + overlayParams.height);
    }

    private View createOverlayContainer(boolean clickThrough) {
        LinearLayout container = new LinearLayout(this);
        container.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(overlayColors[currentColorIndex]);
        bg.setCornerRadius(20);
        bg.setStroke(3, Color.parseColor("#FF6B35"));
        container.setBackground(bg);
        container.setPadding(20, 15, 20, 15);

        TextView label = new TextView(this);
        label.setText(clickThrough ? "点击穿透悬浮窗" : "FloatMask 悬浮窗");
        label.setTextColor(Color.WHITE);
        label.setTextSize(13);
        label.setTag("label");
        container.addView(label);

        TextView info = new TextView(this);
        if (clickThrough) {
            info.setText("点击穿透模式\n触摸事件穿透到下层\n可点击悬浮窗下方内容");
        } else {
            info.setText("拖动：移动悬浮窗\n双指缩放：调整大小\n双击：切换颜色\n长按：打开菜单");
        }
        info.setTextColor(Color.parseColor("#BBBBBB"));
        info.setTextSize(10);
        info.setPadding(0, 5, 0, 0);
        info.setTag("info");
        container.addView(info);

        View sep = new View(this);
        sep.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 2));
        GradientDrawable sepBg = new GradientDrawable();
        sepBg.setColor(Color.parseColor("#FF6B35"));
        sep.setBackground(sepBg);
        container.addView(sep);

        if (!clickThrough) {
            setupDragAndGestures(container);
        }

        return container;
    }

    private void setupDragAndGestures(LinearLayout container) {
        container.setOnTouchListener(new View.OnTouchListener() {
            private float prevX1, prevY1, prevX2, prevY2;
            private boolean multiTouch = false;

            @Override
            public boolean onTouch(View v, MotionEvent event) {
                switch (event.getActionMasked()) {
                    case MotionEvent.ACTION_DOWN:
                        touchDownTime = System.currentTimeMillis();
                        touchDownX = event.getRawX();
                        touchDownY = event.getRawY();
                        lastTouchX = event.getRawX();
                        lastTouchY = event.getRawY();
                        lastViewX = overlayParams.x;
                        lastViewY = overlayParams.y;
                        isDragging = false;
                        isResizing = false;
                        multiTouch = false;
                        return true;

                    case MotionEvent.ACTION_POINTER_DOWN:
                        multiTouch = true;
                        isDragging = false;
                        if (event.getPointerCount() >= 2) {
                            prevX1 = event.getX(0);
                            prevY1 = event.getY(0);
                            prevX2 = event.getX(1);
                            prevY2 = event.getY(1);
                            initialDistance = distance(event.getX(0), event.getY(0),
                                    event.getX(1), event.getY(1));
                            initialWidth = overlayParams.width;
                            initialHeight = overlayParams.height;
                            isResizing = true;
                        }
                        return true;

                    case MotionEvent.ACTION_MOVE:
                        if (isResizing && event.getPointerCount() >= 2) {
                            float currentDistance = distance(
                                    event.getX(0), event.getY(0),
                                    event.getX(1), event.getY(1));
                            float scale = currentDistance / initialDistance;
                            int newW = Math.max(MIN_SIZE, (int)(initialWidth * scale));
                            int newH = Math.max(MIN_SIZE, (int)(initialHeight * scale));
                            overlayParams.width = newW;
                            overlayParams.height = newH;
                            try {
                                windowManager.updateViewLayout(container, overlayParams);
                            } catch (Exception e) {}
                            return true;
                        }

                        if (!multiTouch) {
                            float dx = event.getRawX() - lastTouchX;
                            float dy = event.getRawY() - lastTouchY;
                            if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
                                isDragging = true;
                            }
                            if (isDragging) {
                                int newX = (int)(lastViewX + dx);
                                int newY = (int)(lastViewY + dy);
                                newX = Math.max(-overlayParams.width / 2,
                                        Math.min(newX, screenWidth - overlayParams.width / 2));
                                newY = Math.max(0,
                                        Math.min(newY, screenHeight - overlayParams.height / 2));
                                overlayParams.x = newX;
                                overlayParams.y = newY;
                                try {
                                    windowManager.updateViewLayout(container, overlayParams);
                                } catch (Exception e) {}
                            }
                        }
                        return true;

                    case MotionEvent.ACTION_POINTER_UP:
                        isResizing = false;
                        return true;

                    case MotionEvent.ACTION_UP:
                        long tapDuration = System.currentTimeMillis() - touchDownTime;
                        float moveDistance = distance(touchDownX, touchDownY,
                                event.getRawX(), event.getRawY());

                        if (!isDragging && !isResizing && !multiTouch) {
                            if (tapDuration < DOUBLE_TAP_TIMEOUT) {
                                long now = System.currentTimeMillis();
                                if (now - lastTapTime < DOUBLE_TAP_TIMEOUT * 2) {
                                    onDoubleTap(container);
                                    lastTapTime = 0;
                                    return true;
                                }
                                lastTapTime = now;
                                handler.postDelayed(() -> {
                                    if (lastTapTime != 0) {
                                        lastTapTime = 0;
                                    }
                                }, DOUBLE_TAP_TIMEOUT * 2);
                            } else if (tapDuration > LONG_PRESS_TIMEOUT && moveDistance < 20) {
                                onLongPress(container);
                            }
                        }
                        isDragging = false;
                        isResizing = false;
                        multiTouch = false;
                        return true;
                }
                return false;
            }
        });
    }

    private float distance(float x1, float y1, float x2, float y2) {
        float dx = x1 - x2;
        float dy = y1 - y2;
        return (float) Math.sqrt(dx * dx + dy * dy);
    }

    private void onDoubleTap(LinearLayout container) {
        currentColorIndex = (currentColorIndex + 1) % overlayColors.length;
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(overlayColors[currentColorIndex]);
        bg.setCornerRadius(20);
        bg.setStroke(3, Color.parseColor("#FF6B35"));
        container.setBackground(bg);
        Toast.makeText(this, "颜色：" + (currentColorIndex + 1) + "/" + overlayColors.length,
                Toast.LENGTH_SHORT).show();
        Log.i(TAG, "Color changed to index " + currentColorIndex);
    }

    private void onLongPress(LinearLayout container) {
        Toast.makeText(this, "长按 - 打开菜单", Toast.LENGTH_SHORT).show();
        showQuickMenu(container);
    }

    private void showQuickMenu(LinearLayout overlayContainer) {
        if (quickMenuView != null) {
            try { windowManager.removeView(quickMenuView); } catch (Exception e) {}
            quickMenuView = null;
        }

        quickMenuView = new LinearLayout(this);
        quickMenuView.setOrientation(LinearLayout.VERTICAL);

        GradientDrawable menuBg = new GradientDrawable();
        menuBg.setColor(Color.parseColor("#F5F5F5"));
        menuBg.setCornerRadius(16);
        menuBg.setStroke(2, Color.parseColor("#FF6B35"));
        quickMenuView.setBackground(menuBg);
        quickMenuView.setPadding(16, 12, 16, 12);

        TextView menuTitle = new TextView(this);
        menuTitle.setText("快捷菜单");
        menuTitle.setTextSize(14);
        menuTitle.setTextColor(Color.BLACK);
        menuTitle.setPadding(0, 0, 0, 8);
        quickMenuView.addView(menuTitle);

        View sep1 = new View(this);
        sep1.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1));
        GradientDrawable sepBg1 = new GradientDrawable();
        sepBg1.setColor(Color.parseColor("#E0E0E0"));
        sep1.setBackground(sepBg1);
        quickMenuView.addView(sep1);

        addMenuItem("切换颜色", v -> {
            onDoubleTap(overlayContainer);
            closeQuickMenu();
        });

        addMenuItem("尺寸：小", v -> {
            overlayParams.width = 250;
            overlayParams.height = 300;
            try { windowManager.updateViewLayout(overlayContainer, overlayParams); } catch (Exception e) {}
            closeQuickMenu();
        });

        addMenuItem("尺寸：中", v -> {
            overlayParams.width = 400;
            overlayParams.height = 600;
            try { windowManager.updateViewLayout(overlayContainer, overlayParams); } catch (Exception e) {}
            closeQuickMenu();
        });

        addMenuItem("尺寸：大", v -> {
            overlayParams.width = 600;
            overlayParams.height = 800;
            try { windowManager.updateViewLayout(overlayContainer, overlayParams); } catch (Exception e) {}
            closeQuickMenu();
        });

        addMenuItem("透明度：50%", v -> {
            containerSetAlpha(overlayContainer, 0.5f);
            closeQuickMenu();
        });

        addMenuItem("透明度：100%", v -> {
            containerSetAlpha(overlayContainer, 1.0f);
            closeQuickMenu();
        });

        addMenuItem("关闭", v -> {
            closeQuickMenu();
            hideOverlay();
        });

        WindowManager.LayoutParams menuParams = new WindowManager.LayoutParams(
                300,
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
                PixelFormat.TRANSLUCENT);
        menuParams.gravity = Gravity.TOP | Gravity.START;
        menuParams.x = Math.min(overlayParams.x + 50, screenWidth - 320);
        menuParams.y = overlayParams.y + overlayParams.height + 10;
        if (menuParams.y + 500 > screenHeight) {
            menuParams.y = Math.max(0, overlayParams.y - 400);
        }

        quickMenuView.setTag(menuParams);
        windowManager.addView(quickMenuView, menuParams);
        Log.i(TAG, "Quick menu shown");
    }

    private void containerSetAlpha(LinearLayout container, float alpha) {
        container.setAlpha(alpha);
    }

    private void addMenuItem(String text, View.OnClickListener listener) {
        TextView item = new TextView(this);
        item.setText(text);
        item.setTextSize(13);
        item.setTextColor(Color.parseColor("#333333"));
        item.setPadding(12, 10, 12, 10);
        item.setOnClickListener(listener);

        GradientDrawable itemBg = new GradientDrawable();
        itemBg.setColor(Color.TRANSPARENT);
        itemBg.setCornerRadius(8);
        item.setBackground(itemBg);
        quickMenuView.addView(item);

        View sep = new View(this);
        sep.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 1));
        GradientDrawable sepBg = new GradientDrawable();
        sepBg.setColor(Color.parseColor("#EEEEEE"));
        sep.setBackground(sepBg);
        quickMenuView.addView(sep);
    }

    private void closeQuickMenu() {
        if (quickMenuView != null) {
            try { windowManager.removeView(quickMenuView); } catch (Exception e) {}
            quickMenuView = null;
        }
    }

    private void hideOverlay() {
        closeQuickMenu();
        if (overlayView != null && isOverlayShowing) {
            try {
                windowManager.removeView(overlayView);
            } catch (Exception e) {
                Log.e(TAG, "Error removing overlay", e);
            }
            overlayView = null;
            isOverlayShowing = false;
            isMinimized = false;
            statusText.setText("悬浮窗已隐藏");
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        hideOverlay();
    }
}

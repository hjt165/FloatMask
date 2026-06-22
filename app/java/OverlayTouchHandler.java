package com.floatmask.overlay;

import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.os.Handler;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;

/**
 * 原生悬浮窗触摸事件处理器
 * 检测拖拽、双击、长按、多指缩放等手势
 * 通过静态回调与Python/Pyjnius通信
 */
public class OverlayTouchHandler implements View.OnTouchListener {

    private static final long DOUBLE_TAP_TIMEOUT = 300;
    private static final long LONG_PRESS_TIMEOUT = 500;
    private static final int MIN_OVERLAY_SIZE = 80;
    private static final float DRAG_THRESHOLD = 5f;

    private final WindowManager windowManager;
    private final WindowManager.LayoutParams params;
    private final View overlayView;
    private final int screenWidth;
    private final int screenHeight;

    private float lastTouchX, lastTouchY;
    private int lastViewX, lastViewY;
    private boolean isDragging = false;
    private boolean isResizing = false;
    private boolean multiTouch = false;
    private long touchDownTime = 0;
    private float touchDownX, touchDownY;
    private long lastTapTime = 0;

    private float initialDistance;
    private int initialWidth, initialHeight;

    private static OverlayTouchHandler instance;
    private static TouchCallback callback;

    private final Handler handler = new Handler();
    private boolean isMinimized = false;
    private int currentColorIndex = 0;

    public interface TouchCallback {
        void onDoubleTap();
        void onLongPress();
        void onDragStart();
        void onDragEnd(int x, int y);
        void onResize(int width, int height);
    }

    public OverlayTouchHandler(WindowManager wm, WindowManager.LayoutParams p,
                                View view, int screenW, int screenH) {
        this.windowManager = wm;
        this.params = p;
        this.overlayView = view;
        this.screenWidth = screenW;
        this.screenHeight = screenH;
        instance = this;
    }

    public static void setCallback(TouchCallback cb) {
        callback = cb;
    }

    public static OverlayTouchHandler getInstance() {
        return instance;
    }

    public void setColorIndex(int index) {
        this.currentColorIndex = index;
    }

    public int getColorIndex() {
        return currentColorIndex;
    }

    @Override
    public boolean onTouch(View v, MotionEvent event) {
        switch (event.getActionMasked()) {
            case MotionEvent.ACTION_DOWN:
                touchDownTime = System.currentTimeMillis();
                touchDownX = event.getRawX();
                touchDownY = event.getRawY();
                lastTouchX = event.getRawX();
                lastTouchY = event.getRawY();
                lastViewX = params.x;
                lastViewY = params.y;
                isDragging = false;
                isResizing = false;
                multiTouch = false;
                return true;

            case MotionEvent.ACTION_POINTER_DOWN:
                multiTouch = true;
                isDragging = false;
                if (event.getPointerCount() >= 2) {
                    initialDistance = distance(
                        event.getX(0), event.getY(0),
                        event.getX(1), event.getY(1));
                    if (initialDistance < 1f) {
                        initialDistance = 1f;
                    }
                    initialWidth = params.width;
                    initialHeight = params.height;
                    isResizing = true;
                }
                return true;

            case MotionEvent.ACTION_MOVE:
                if (isResizing && event.getPointerCount() >= 2) {
                    float currentDistance = distance(
                        event.getX(0), event.getY(0),
                        event.getX(1), event.getY(1));
                    float scale = currentDistance / initialDistance;
                    int newW = Math.max(MIN_OVERLAY_SIZE, (int)(initialWidth * scale));
                    int newH = Math.max(MIN_OVERLAY_SIZE, (int)(initialHeight * scale));
                    params.width = newW;
                    params.height = newH;
                    try {
                        windowManager.updateViewLayout(overlayView, params);
                    } catch (Exception e) {}
                    if (callback != null) {
                        callback.onResize(newW, newH);
                    }
                    return true;
                }

                if (!multiTouch) {
                    float dx = event.getRawX() - lastTouchX;
                    float dy = event.getRawY() - lastTouchY;
                    if (Math.abs(dx) > DRAG_THRESHOLD || Math.abs(dy) > DRAG_THRESHOLD) {
                        if (!isDragging) {
                            isDragging = true;
                            if (callback != null) callback.onDragStart();
                        }
                    }
                    if (isDragging) {
                        int newX = (int)(lastViewX + dx);
                        int newY = (int)(lastViewY + dy);
                        newX = Math.max(-params.width / 2,
                                Math.min(newX, screenWidth - params.width / 2));
                        newY = Math.max(0,
                                Math.min(newY, screenHeight - params.height / 2));
                        params.x = newX;
                        params.y = newY;
                        try {
                            windowManager.updateViewLayout(overlayView, params);
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
                            lastTapTime = 0;
                            if (callback != null) callback.onDoubleTap();
                            return true;
                        }
                        lastTapTime = now;
                        handler.postDelayed(() -> {
                            if (lastTapTime != 0) {
                                lastTapTime = 0;
                            }
                        }, DOUBLE_TAP_TIMEOUT * 2);
                    } else if (tapDuration > LONG_PRESS_TIMEOUT && moveDistance < 20) {
                        if (callback != null) callback.onLongPress();
                    }
                }

                if (isDragging && callback != null) {
                    callback.onDragEnd(params.x, params.y);
                }

                isDragging = false;
                isResizing = false;
                multiTouch = false;
                return true;
        }
        return false;
    }

    private float distance(float x1, float y1, float x2, float y2) {
        float dx = x1 - x2;
        float dy = y1 - y2;
        return (float) Math.sqrt(dx * dx + dy * dy);
    }
}

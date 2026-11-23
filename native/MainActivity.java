package com.muraj3ti.murajaati;

import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.WebView;
import android.widget.ImageView;

import androidx.core.splashscreen.SplashScreen;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;

import com.getcapacitor.BridgeActivity;

/**
 * شاشة البداية: نظام أندرويد 12+ يعرض أيقونة التطبيق على خلفية سادة ولا يسمح بصورة كاملة،
 * لذلك نجعل شاشة النظام سادة بلون الخلفية (انظر styles.xml)، ثم نعرض صورتنا (drawable/splash)
 * كاملة الشاشة فوق الـ WebView حتى تنتهي الصفحة من التحميل، ثم تتلاشى لتظهر شاشة splash الخاصة بالصفحة.
 */
public class MainActivity extends BridgeActivity {

    private static final long MIN_SHOW_MS = 700;   // أقل مدة عرض لتفادي الوميض
    private static final long MAX_SHOW_MS = 9000;  // حدّ أقصى إن تعذّر التحميل
    private static final long FADE_MS = 400;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private ImageView splash;
    private long shownAt;
    private boolean closing;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);
        if (savedInstanceState == null) {
            showSplash();
        }
    }

    private void showSplash() {
        shownAt = System.currentTimeMillis();
        splash = new ImageView(this);
        splash.setBackgroundColor(0xFF041029);
        splash.setScaleType(ImageView.ScaleType.CENTER_CROP);
        splash.setImageResource(R.drawable.splash);
        splash.setClickable(true);
        addContentView(splash, new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        setFullscreen(true);
        handler.postDelayed(checker, MIN_SHOW_MS);
    }

    private final Runnable checker = new Runnable() {
        @Override
        public void run() {
            long elapsed = System.currentTimeMillis() - shownAt;
            boolean loaded = false;
            try {
                WebView wv = getBridge() != null ? getBridge().getWebView() : null;
                loaded = wv != null && wv.getProgress() >= 100;
            } catch (Throwable ignored) {
            }
            if ((loaded && elapsed >= MIN_SHOW_MS) || elapsed >= MAX_SHOW_MS) {
                dismissSplash();
            } else {
                handler.postDelayed(this, 100);
            }
        }
    };

    private void dismissSplash() {
        if (closing || splash == null) return;
        closing = true;
        setFullscreen(false);
        final ImageView v = splash;
        v.animate().alpha(0f).setDuration(FADE_MS).withEndAction(new Runnable() {
            @Override
            public void run() {
                if (v.getParent() instanceof ViewGroup) {
                    ((ViewGroup) v.getParent()).removeView(v);
                }
                splash = null;
            }
        }).start();
    }

    /** إخفاء شريطي الحالة والتنقل أثناء الـ splash ليظهر كامل الشاشة، ثم إرجاعهما. */
    private void setFullscreen(boolean on) {
        Window w = getWindow();
        if (Build.VERSION.SDK_INT >= 28) {
            WindowManager.LayoutParams lp = w.getAttributes();
            lp.layoutInDisplayCutoutMode = on
                    ? WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                    : WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_DEFAULT;
            w.setAttributes(lp);
        }
        WindowInsetsControllerCompat c = WindowCompat.getInsetsController(w, w.getDecorView());
        if (c == null) return;
        if (on) {
            c.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            c.hide(WindowInsetsCompat.Type.systemBars());
        } else {
            c.show(WindowInsetsCompat.Type.systemBars());
        }
    }

    @Override
    public void onDestroy() {
        handler.removeCallbacks(checker);
        super.onDestroy();
    }
}

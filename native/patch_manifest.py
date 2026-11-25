#!/usr/bin/env python3
"""يعدّل AndroidManifest.xml أثناء البناء:
1) رابط العودة من كروم (com.muraj3ti.murajaati://auth)
2) إذن الميكروفون + خدمة التعرّف الصوتي (للمسمّع الآلي)
كل جزء يُضاف فقط إن لم يكن موجوداً، فتشغيل الملف مرتين آمن."""
import re, sys

path = sys.argv[1]
src = open(path, encoding="utf-8").read()
changed = []

# ---------- 1) رابط العودة ----------
FILTER = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="com.muraj3ti.murajaati" android:host="auth" />
            </intent-filter>
'''
if 'android:scheme="com.muraj3ti.murajaati"' not in src:
    i = src.find("</intent-filter>")
    if i < 0:
        sys.exit("ERROR: no intent-filter found in manifest")
    i += len("</intent-filter>")
    src = src[:i] + FILTER + src[i:]
    act = re.search(r"<activity\b[^>]*>", src)
    if act and "launchMode" not in act.group(0):
        src = src.replace(act.group(0), act.group(0)[:-1] + ' android:launchMode="singleTask">', 1)
    changed.append("deep link")

# ---------- 2) الميكروفون والتعرّف الصوتي ----------
app_pos = src.find("<application")
if app_pos < 0:
    sys.exit("ERROR: no <application> tag in manifest")

perms = ""
for p in ("android.permission.RECORD_AUDIO", "android.permission.MODIFY_AUDIO_SETTINGS"):
    if p not in src:
        perms += '    <uses-permission android:name="%s" />\n' % p
        changed.append(p)

queries_intent = '<intent><action android:name="android.speech.RecognitionService" /></intent>'
queries = ""
if "android.speech.RecognitionService" not in src:
    if "<queries>" in src:
        src = src.replace("<queries>", "<queries>\n        " + queries_intent, 1)
        app_pos = src.find("<application")
    else:
        queries = "    <queries>\n        " + queries_intent + "\n    </queries>\n"
    changed.append("speech queries")

if perms or queries:
    src = src[:app_pos] + perms + queries + "\n    " + src[app_pos:]

open(path, "w", encoding="utf-8").write(src)
print("manifest patched:", ", ".join(changed) if changed else "nothing to change")

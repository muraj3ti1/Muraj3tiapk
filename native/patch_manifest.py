#!/usr/bin/env python3
"""يعدّل AndroidManifest.xml: رابط العودة من كروم + singleTask + إذن الميكروفون وخدمة التعرّف الصوتي.
كل جزء يُفحص على حدة فلا يتكرر شيء."""
import re, sys

path = sys.argv[1]
src = open(path, encoding="utf-8").read()
changed = []

FILTER = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="com.muraj3ti.murajaati" android:host="auth" />
            </intent-filter>
'''

# 1) رابط العودة (كما كان)
if 'android:scheme="com.muraj3ti.murajaati"' not in src:
    i = src.find("</intent-filter>")
    if i < 0:
        sys.exit("ERROR: no intent-filter found in manifest")
    i += len("</intent-filter>")
    src = src[:i] + FILTER + src[i:]
    changed.append("deep link")

# 2) singleTask (كما كان)
act = re.search(r"<activity\b[^>]*>", src)
if act and "launchMode" not in act.group(0):
    src = src.replace(act.group(0), act.group(0)[:-1] + ' android:launchMode="singleTask">', 1)
    changed.append("singleTask")

# 3) الأذونات (جديد)
for perm in ("android.permission.RECORD_AUDIO", "android.permission.MODIFY_AUDIO_SETTINGS"):
    if perm not in src:
        m = re.search(r"<manifest\b[^>]*>", src)
        if not m:
            sys.exit("ERROR: no <manifest> tag")
        line = '\n    <uses-permission android:name="%s" />' % perm
        src = src[:m.end()] + line + src[m.end():]
        changed.append(perm)

# 4) رؤية خدمة التعرّف الصوتي (جديد)
if "android.speech.RecognitionService" not in src:
    q = '\n    <queries>\n        <intent><action android:name="android.speech.RecognitionService" /></intent>\n    </queries>'
    j = src.rfind("</manifest>")
    if j < 0:
        sys.exit("ERROR: no </manifest>")
    src = src[:j] + q + "\n" + src[j:]
    changed.append("queries")

open(path, "w", encoding="utf-8").write(src)
print("manifest patched:", ", ".join(changed) if changed else "nothing to do")

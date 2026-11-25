#!/usr/bin/env python3
"""يعدّل AndroidManifest.xml أثناء البناء. كل خطوة آمنة لإعادة التشغيل (لا تتكرر):
   1) رابط العودة من متصفح كروم لتسجيل Google (com.muraj3ti.murajaati://auth)
   2) إذن الميكروفون للمسمّع الآلي (RECORD_AUDIO) وإتاحة خدمة التعرّف الصوتي للتطبيق
   وفي النهاية يتأكد أن الملف سليم، وإلا يفشل البناء بدل أن يُنشر تطبيق معطوب."""
import re, sys
from xml.dom import minidom

path = sys.argv[1]
src = open(path, encoding="utf-8").read()

# ---------- 1) رابط تسجيل Google ----------
FILTER = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="com.muraj3ti.murajaati" android:host="auth" />
            </intent-filter>
'''
if 'android:scheme="com.muraj3ti.murajaati"' in src:
    print("deep link already present")
else:
    # بعد أول </intent-filter> (فلتر MAIN/LAUNCHER) داخل الـ activity الرئيسي
    i = src.find("</intent-filter>")
    if i < 0:
        sys.exit("ERROR: no intent-filter found in manifest")
    i += len("</intent-filter>")
    src = src[:i] + FILTER + src[i:]
    # لازم singleTask كي يصل الرابط إلى النسخة المفتوحة من التطبيق
    act = re.search(r"<activity\b[^>]*>", src)
    if act and "launchMode" not in act.group(0):
        src = src.replace(act.group(0), act.group(0)[:-1] + ' android:launchMode="singleTask">', 1)
    print("deep link added")

# ---------- 2) إذن الميكروفون للمسمّع الآلي ----------
PERMS = ["android.permission.RECORD_AUDIO", "android.permission.MODIFY_AUDIO_SETTINGS"]
add = "".join('<uses-permission android:name="%s" />\n    ' % p for p in PERMS if p not in src)
if add:
    i = src.find("<application")
    if i < 0:
        sys.exit("ERROR: no <application> tag in manifest")
    src = src[:i] + add + src[i:]
    print("permissions added")
else:
    print("permissions already present")

QI = '<intent>\n            <action android:name="android.speech.RecognitionService" />\n        </intent>'
if "android.speech.RecognitionService" not in src:
    if "<queries>" in src:
        src = src.replace("<queries>", "<queries>\n        " + QI, 1)
    else:
        j = src.rfind("</manifest>")
        if j < 0:
            sys.exit("ERROR: no </manifest> in manifest")
        src = src[:j] + "    <queries>\n        " + QI + "\n    </queries>\n" + src[j:]
    print("queries added")
else:
    print("queries already present")

# ---------- تحقق نهائي ----------
try:
    minidom.parseString(src.encode("utf-8"))
except Exception as e:
    sys.exit("ERROR: manifest is not valid XML after patch: %s" % e)
for p in PERMS:
    assert p in src, p

open(path, "w", encoding="utf-8").write(src)
print("manifest patched")

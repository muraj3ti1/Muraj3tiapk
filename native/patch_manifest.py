#!/usr/bin/env python3
"""يضيف رابط العودة من متصفح كروم (com.muraj3ti.murajaati://auth) إلى AndroidManifest.xml."""
import re, sys

path = sys.argv[1]
src = open(path, encoding="utf-8").read()

if 'android:scheme="com.muraj3ti.murajaati"' in src:
    print("deep link already present")
    sys.exit(0)

FILTER = '''
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="com.muraj3ti.murajaati" android:host="auth" />
            </intent-filter>
'''

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

open(path, "w", encoding="utf-8").write(src)
print("manifest patched")

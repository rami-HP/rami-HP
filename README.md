# Rami HP Project

This repository includes a small script that calls the OpenAI API. It is configured to run on GitHub Actions using Python 3.11.

Requirements
- Python 3.11
- Install dependencies:
  pip install -r requirements.txt

Set OPENAI_API_KEY (GitHub Actions)
- Via the web UI:
  Settings → Secrets and variables → Actions → New repository secret  
  Name: OPENAI_API_KEY  
  Value: <your OpenAI API key from openai.com>

- Or via GitHub CLI:
  gh secret set OPENAI_API_KEY --body "sk-..." --repo rami-HP/rami-HP

Usage (local)
- Linux / macOS / Windows:
  (PowerShell) $env:OPENAI_API_KEY="sk-..."; python custom\key_id\model_id.py
  (cmd) set OPENAI_API_KEY=sk-... && python custom\key_id\model_id.py

Notes
- The workflow file (.github/workflows/ci.yml) runs Python 3.11 and executes custom/key_id/model_id.py using the OPENAI_API_KEY secret.
- The default model in the script is gpt-3.5-turbo; you can change it via the OPENAI_MODEL env var or by editing the code.
- Do NOT commit your API key into the repository.

---

# مشروع Rami HP

يحتوي هذا المستودع على سكربت بسيط يستدعي واجهة برمجة تطبيقات OpenAI. مُعدّ للتشغيل على GitHub Actions باستخدام Python 3.11.

المتطلبات
- Python 3.11
- تثبيت الاعتماديات:
  pip install -r requirements.txt

تعيين OPENAI_API_KEY (لـ GitHub Actions)
- عبر واجهة الويب:
  Settings → Secrets and variables → Actions → New repository secret  
  الاسم: OPENAI_API_KEY  
  القيمة: <مفتاح OpenAI الخاص بك من openai.com>

- أو عبر GitHub CLI:
  gh secret set OPENAI_API_KEY --body "sk-..." --repo rami-HP/rami-HP

الاستخدام محلياً
- نظام Linux / macOS / Windows:
  (PowerShell) $env:OPENAI_API_KEY="sk-..."; python custom\key_id\model_id.py
  (cmd) set OPENAI_API_KEY=sk-... && python custom\key_id\model_id.py

ملاحظات
- ملف سير العمل (.github/workflows/ci.yml) يقوم بتشغيل Python 3.11 وينفّذ custom/key_id/model_id.py مستخدماً السر OPENAI_API_KEY.
- اسم النموذج الافتراضي في السكربت هو gpt-3.5-turbo؛ يمكن تغييره عبر متغير البيئة OPENAI_MODEL أو تعديل الكود.
- لا تُضمّن مفتاح API داخل المستودع.
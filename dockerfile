# ============================================================
# HB-Eval System – Open-Core Edition
# Official Docker Image (Multi-stage build – أصغر حجم + أكثر أمانًا)
# Python 3.11 Slim → ~85 MB فقط
# ============================================================

# ──────── Stage 1: Build ────────
FROM python:3.11-slim AS builder

# تحسين الأداء + منع الكاش
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# تثبيت الأدوات المطلوبة لبناء الويلز (إن وجدت)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# نسخ ملفات الاعتماد أولًا (لاستغلال الكاش)
COPY pyproject.toml setup.py README.md ./
COPY open_core ./open_core

# تثبيت الاعتماديات + الحزمة
RUN pip install --upgrade pip && \
    pip install .

# ──────── Stage 2: Runtime (الصورة النهائية النحيفة جدًا) ────────
FROM python:3.11-slim

# إنشاء مستخدم غير root (أفضل ممارسة أمنية 2025)
RUN adduser --disabled-password --gecos '' hbuser

WORKDIR /app

# نسخ فقط الملفات المطلوبة من مرحلة البناء
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/open_core ./open_core

# تبديل للمستخدم غير root
USER hbuser

# متغيّر بيئي لتفعيل وضع الإنتاج
ENV HB_EVAL_MODE=production

# رسالة ترحيبية عند التشغيل
ENTRYPOINT ["python", "-c", "from open_core.demo import run_demo; run_demo()"]

# إذا أراد المستخدم تشغيل أمر مخصص
CMD ["python", "-c", "print('HB-Eval System Open-Core ready! Run: from open_core.demo import run_demo; run_demo()')"]

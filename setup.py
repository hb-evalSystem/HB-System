# setup.py – HB-Eval System (Open-Core Edition)
# Python 3.8+ | Apache 2.0 with commercial restrictions

from setuptools import setup, find_packages
from pathlib import Path

# =========================================================
# قراءة README + LICENSE للنشر على PyPI
# =========================================================
BASE_DIR = Path(__file__).parent

README = (BASE_DIR / "README.md").read_text(encoding="utf-8")
LICENSE_TEXT = (BASE_DIR / "LICENSE").read_text(encoding="utf-8")

# =========================================================
# إعدادات الـ setup النهائية
# =========================================================
setup(
    name="hb-eval-system",                    # اسم أجمل وأقوى تجاريًا
    version="0.1.0",                          # إزالة beta للانطباع الأول القوي
    description="Leading behavioral evaluation & trustworthy agentic AI system (Open-Core)",
    long_description=README,
    long_description_content_type="text/markdown",

    author="Abuelgasim Mohamed Ibrahim Adam",
    author_email="contact@hb-eval.ai",        # بريد احترافي
    url="https://github.com/hb-eval/system",
    project_urls={
        "Documentation": "https://github.com/hb-eval/system#readme",
        "Source": "https://github.com/hb-eval/system",
        "Commercial": "mailto:licensing@hb-eval.ai",
        "arXiv Series": "https://arxiv.org/search/cs?query=hb-eval",
    },

    packages=find_packages(include=["open_core", "open_core.*"]),
    include_package_data=True,                # مهم لتضمين README + LICENSE

    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21",
        "requests>=2.28",
    ],

    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "docs": ["mkdocs", "mkdocstrings"],
    },

    license="Apache-2.0",
    license_files=["LICENSE"],                # يضمن رفع ملف الترخيص مع الحزمة

    keywords=[
        "agentic-ai", "cognitive-architecture", "xai", "llm-agents",
        "adaptive-planning", "behavioral-evaluation", "trustworthy-ai",
        "pei", "frr", "hci-edm", "edm-memory"
    ],

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    entry_points={
        "console_scripts": [
            "hb-eval-demo=open_core.demo:run_demo",   # يسمح بتشغيل: hb-eval-demo
        ],
    },
)

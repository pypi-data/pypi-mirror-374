# setup.py

from setuptools import setup, find_packages

# خواندن محتوای فایل README.md برای توضیحات کامل در PyPI
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sparrow-lib",  # نامی که با pip نصب می‌شود (باید در PyPI منحصر به فرد باشد)
    version="2.0.3",      # نسخه اولیه
    author="AmirReza",  # نام شما
    author_email="amirrezaahali@gmail.com", # ایمیل شما
    description="A library to augment LLMs with dynamic, trainable routers for efficient fine-tuning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="", # آدرس پروژه در گیت‌هاب
    packages=find_packages(), # به طور خودکار پکیج sparrow را پیدا می‌کند
    install_requires=[
        "torch>=1.9.0",
        "transformers>=4.10.0",
        "pandas",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires='>=3.7',
)
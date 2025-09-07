from setuptools import setup, find_packages

setup(
    name="vezor_sdk",
    version="0.1.2",
    description="Bridge Python SDK da Vezor",
    author="Breno Leone",
    author_email="admin.platform@vezor.com.br",
    url="https://github.com/vezor-group/vezor_sdk",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["requests>=2.31.0"],
    python_requires=">=3.8",
    license="MIT",
)

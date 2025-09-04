"""
# 打包命令
python setup.py sdist bdist_wheel
# 上传命令
twine upload dist/* --verbose

pypi-AgEIcHlwaS5vcmcCJDUxZGVmYjczLWU5NTgtNGE0Yi1hYmJkLTAwNmM5OGI4ZWVlOQACDlsxLFsiZGJnb25lIl1dAAIsWzIsWyJiZGMyZDZlNy0xYTYxLTQwMGUtODc0MS1mMWJmNjI4NTIzNzciXV0AAAYgMiOxGI2LUsyRpMVrWEBVYxh-UQM4UMABYSlpGJ-bIqo
"""

import os, shutil
from setuptools import setup


name = "dbgone"
version = "0.0.1a2"
packages = [
    "dbgone",
    "dbgone.config",
    "dbgone.optuna",
    "dbgone.torch"
]


def del_setuptools_pycache():
    # 删除setup.py文件构建的build, dist, viutils.egg-info文件夹
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists(f"{name}.egg-info"):
        shutil.rmtree(f"{name}.egg-info")


def del_pycache(path):
    # 递归删除每个子文件夹的__pycache__
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            if dir == "__pycache__":
                shutil.rmtree(os.path.join(root, dir))
            else:
                del_pycache(os.path.join(root, dir))


def main():
    del_setuptools_pycache()
    with open("requirements.txt", "r", encoding="utf-8") as f:
        install_requires = [
            l
            for l in f.read().splitlines()
            if not l.startswith("#") and l.strip() != ""
        ]

    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

    del_pycache(name)  # 删除每个子文件夹的__pycache__文件夹

    setup(
        name=name,
        version=version,
        long_description=long_description,
        long_description_content_type="text/markdown",
        description="A common library frequently used on python",
        url="https://github.com/Viyyy/dbgone",
        author="Re.VI",
        author_email="another91026@gmail.com",
        license="Apache License 2.0",
        packages=packages,
        install_requires=install_requires,
        extras_require={
            "torch": [
                "torch",
            ]
        },
        zip_safe=False,
    )

if __name__=="__main__":
    main()
    print("打包成功！")
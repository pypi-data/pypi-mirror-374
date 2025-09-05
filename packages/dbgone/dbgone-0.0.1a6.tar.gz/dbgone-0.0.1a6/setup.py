"""
# 打包命令
python setup.py sdist bdist_wheel
# 上传命令
twine upload dist/* --verbose

pypi-AgEIcHlwaS5vcmcCJDUxZGVmYjczLWU5NTgtNGE0Yi1hYmJkLTAwNmM5OGI4ZWVlOQACDlsxLFsiZGJnb25lIl1dAAIsWzIsWyJiZGMyZDZlNy0xYTYxLTQwMGUtODc0MS1mMWJmNjI4NTIzNzciXV0AAAYgMiOxGI2LUsyRpMVrWEBVYxh-UQM4UMABYSlpGJ-bIqo

pypi-AgEIcHlwaS5vcmcCJDM4ZGVkMTg4LWNmZmMtNDgyYy1hZjQ3LWIwYTIxMGVhZjVjYQACDlsxLFsiZGJnb25lIl1dAAIsWzIsWyJiZGMyZDZlNy0xYTYxLTQwMGUtODc0MS1mMWJmNjI4NTIzNzciXV0AAAYgLI_Bev-KS0fGcyjE-a4nXYeixqbfXIL-beb_afJ6C40
"""

import os, shutil
from setuptools import setup


name = "dbgone"
version = "0.0.1a6"

def find_packages_custom():
    """
    自定义函数，遍历 `NAME` 目录，找到所有包含 __init__.py 的文件夹。

    返回:
    list: 包含所有找到的包名的列表。
    """
    base_dir = os.path.dirname(__file__)
    root_dir = os.path.join(base_dir, name)
    packages = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__init__.py" in filenames:  # 如果文件夹包含 __init__.py
            package = ".".join(
                [d for d in dirpath.replace(base_dir, "").split(os.sep) if d.strip()]
            )  # 将路径转换为包名（用点号分隔）
            packages.append(package)
    return packages


# # 遍历 packages_dir 下面的所有文件夹，并将文件夹名作为包名
# # 如果不想打包某些文件夹，可以在这里手动设置或过滤
# # 使用自定义函数查找包
# packages = find_packages_custom()

packages = [
    "dbgone",
    "dbgone.config",
    "dbgone.opt",
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
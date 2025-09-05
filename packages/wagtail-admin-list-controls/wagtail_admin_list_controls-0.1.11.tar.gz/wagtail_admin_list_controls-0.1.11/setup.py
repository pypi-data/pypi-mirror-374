from setuptools import setup
import admin_list_controls


install_requires = [
    "Django>=4.2",
    "wagtail>=6.0",
    "wagtail-modeladmin>=2.0",
]
testing_requires = ["django-webtest"]

setup(
    name="wagtail-admin-list-controls",
    version=admin_list_controls.__version__,
    packages=["admin_list_controls"],
    include_package_data=True,
    description=(
        "A UI toolkit to build custom filtering and other functionalities into "
        "wagtail's admin list views."
    ),
    long_description=(
        "Documentation at https://github.com/ixc/wagtail-admin-list-controls"
    ),
    author="The Interaction Consortium",
    author_email="studio@interaction.net.au",
    url="https://github.com/ixc/wagtail-admin-list-controls",
    install_requires=install_requires,
    license="MIT",
    extras_require={"testing": testing_requires},
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 6",
        "Framework :: Wagtail :: 7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)

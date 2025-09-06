import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-cross-account-route53",
    "version": "1.0.2",
    "description": "CDK Construct to allow creation of Route 53 records in a different account",
    "license": "Apache-2.0",
    "url": "https://github.com/johnf/cdk-cross-account-route53.git",
    "long_description_content_type": "text/markdown",
    "author": "John Ferlito<johnf@inodes.org>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/johnf/cdk-cross-account-route53.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_cross_account_route53",
        "cdk_cross_account_route53._jsii"
    ],
    "package_data": {
        "cdk_cross_account_route53._jsii": [
            "cdk-cross-account-route53@1.0.2.jsii.tgz"
        ],
        "cdk_cross_account_route53": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.82.0, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.114.1, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)

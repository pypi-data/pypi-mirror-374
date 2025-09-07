import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk-codeartifact",
    "version": "1.1.0",
    "description": "This is an AWS CDK Construct to create a new AWS Codeartifact Domain and one or more Repositories",
    "license": "Apache-2.0",
    "url": "https://github.com/walmsles/cdk-codeartifact",
    "long_description_content_type": "text/markdown",
    "author": "Michael Walmsley (@walmsles)<2704782+walmsles@users.noreply.github.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/walmsles/cdk-codeartifact"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk_artifact",
        "cdk_artifact._jsii"
    ],
    "package_data": {
        "cdk_artifact._jsii": [
            "cdk-codeartifact@1.1.0.jsii.tgz"
        ],
        "cdk_artifact": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.214.0, <3.0.0",
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

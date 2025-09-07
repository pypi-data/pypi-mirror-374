r'''
# cdk-codeartifact

CDK Construct to create an AWS Codeartifact repository.  Construct combines creating both Domain and one or more Repositories into one construct and also provides an enumerated type for public external connections.

There are some additional validations built-in to ensure the construct will deploy correctly:

* Naming convention checks for Codeartifact Domain Name.
* Naming convention checks for Codeartifact Repository Name.
* Passing in more than 1 external repository will throw an error - only 1 external repository is supported by Codeartifact.

## Breaking Changes - Migrating to V1.0.0

**Release 1.0.0 introduces breaking changes** so any project you have created using pre-1.0.0 of cdk-codeartifact should not be upgraded to this version.

Migrating to Version 1.0.0 will require any existing stacks to be removed before upgrading. The Cloudformation composition synthesized in V1.0.0 has a different composition, which means that Cloudformation will detect a change in how the stack is constructed and will try to delete the existing CodeArtifact domain and/or repositories.  This will not be possible if any artifacts have been pushed into the repositories.

The original **CodeArtifact** construct class has been deprecated and is replaced by the **Domain** class which better reflects what this code construct is doing.  For convenience, a **Repository** class has been added so that a stand-alone repository can also be created using this library.  The Repository class is a simple extension of the **CfnRepository** class at this stage without any additional functionality.

All Interface Property structures have been renamed to start with a capital "I" to conform to the usual dotnet convention for interface naming, this will assist when cross-compilation is enabled for this construct.

## External Connection Type

When adding an External Connection to your CodeArtifact repository ensure to make use of the `ExternalRepository` type to define the public external repository comnnection.

```python
export enum ExternalRepository {
  NPM = 'public:npmjs',
  PYPI = 'public:pypi',
  MAVEN_CENTRAL = 'public:msven-central',
  MAVEN_GOOGLE_ANDROID = 'public:maven-googleandroid',
  MAVEN_GRADLE_PLUGINS = 'public:maven-gradleplugins',
  MAVEN_COMMONSWARE = 'public:maven-commonsware',
  NUGET = 'public:nuget-org'
}
```

Currently this construct has been published as an NPM package.

## Installation and Usage

### Typescript

#### Installation

```bash
$ npm install --save cdk-codeartifact
```

#### Usage for CDK V2

```python
import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Domain, ExternalRepository } from 'cdk-codeartifact';
import { Construct } from 'constructs';

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    new Domain(this, id, {
      domainName: 'test-domain',
      repositories: [{
        repositoryName: 'test-repo',
        externalConnections: [ExternalRepository.NPM],
      },
      {
        repositoryName: 'test-repo2',
        externalConnections: [ExternalRepository.PYPI],
      }],
    });
  }
}
```
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_codeartifact as _aws_cdk_aws_codeartifact_ceddda9d
import constructs as _constructs_77d1e7e8


class CodeArtifact(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-codeartifact.CodeArtifact",
):
    '''(deprecated) A Construct that will allow easy setup of an AWS CodeArtifact Repository within a domain.

    :deprecated: CodeArtifact class is replaced by Domain and will be removed in future major release 1.1.0

    :stability: deprecated
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IDomainProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -

        :stability: deprecated
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ba4129b8f188f7b076e9e7ac3139b96bb35845c70146fb34605d476775a4356)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="domainInstance")
    def domain_instance(self) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain:
        '''
        :stability: deprecated
        '''
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnDomain, jsii.get(self, "domainInstance"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "IDomainProps":
        '''
        :stability: deprecated
        '''
        return typing.cast("IDomainProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="repositories")
    def repositories(
        self,
    ) -> typing.List[_aws_cdk_aws_codeartifact_ceddda9d.CfnRepository]:
        '''
        :stability: deprecated
        '''
        return typing.cast(typing.List[_aws_cdk_aws_codeartifact_ceddda9d.CfnRepository], jsii.get(self, "repositories"))


class Domain(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-codeartifact.Domain",
):
    '''CodeArtifact Domain Construct - enables creation of a domain along with zero or more repositories.

    Can be used to create just a domain by passing in no IDomainRepositoryProps elements

    Example::

        new Domain(this, 'MyDomain', {
          domainName: 'my-domain',
          repositories: [{
            repositoryName: 'my-repo',
            externalConnections: [ExternalRepository.NPM]
          }]
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        props: "IDomainProps",
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param props: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9d581239482c4af782583fa3746f835e6fcd25dcf04f9291d316b608712285e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument props", value=props, expected_type=type_hints["props"])
        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="domainInstance")
    def domain_instance(self) -> _aws_cdk_aws_codeartifact_ceddda9d.CfnDomain:
        return typing.cast(_aws_cdk_aws_codeartifact_ceddda9d.CfnDomain, jsii.get(self, "domainInstance"))

    @builtins.property
    @jsii.member(jsii_name="props")
    def props(self) -> "IDomainProps":
        return typing.cast("IDomainProps", jsii.get(self, "props"))

    @builtins.property
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.List["Repository"]:
        return typing.cast(typing.List["Repository"], jsii.get(self, "repositories"))


@jsii.enum(jsii_type="cdk-codeartifact.ExternalRepository")
class ExternalRepository(enum.Enum):
    '''Enumeration providing Typed access to ExternalRepository Names which for L1 construct are magic strings.'''

    NPM = "NPM"
    PYPI = "PYPI"
    MAVEN_CENTRAL = "MAVEN_CENTRAL"
    MAVEN_GOOGLE_ANDROID = "MAVEN_GOOGLE_ANDROID"
    MAVEN_GRADLE_PLUGINS = "MAVEN_GRADLE_PLUGINS"
    MAVEN_COMMONSWARE = "MAVEN_COMMONSWARE"
    NUGET = "NUGET"


@jsii.interface(jsii_type="cdk-codeartifact.IDomainProps")
class IDomainProps(typing_extensions.Protocol):
    '''Properties for creating CodeArtifact Domain using the Domain construct.

    DomainProps extends the L1 CfnDomainProps interface to ensure all CloudFormation capabilities are retained
    '''

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''A string that specifies the name of the requested domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-domainname
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''The key used to encrypt the domain.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-encryptionkey
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="permissionsPolicyDocument")
    def permissions_policy_document(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]]:
        '''The document that defines the resource policy that is set on a domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-permissionspolicydocument
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.Optional[typing.List["IDomainRepositoryProps"]]:
        '''a list of Repositories to create.'''
        ...

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''A list of tags to be applied to the domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-tags
        '''
        ...


class _IDomainPropsProxy:
    '''Properties for creating CodeArtifact Domain using the Domain construct.

    DomainProps extends the L1 CfnDomainProps interface to ensure all CloudFormation capabilities are retained
    '''

    __jsii_type__: typing.ClassVar[str] = "cdk-codeartifact.IDomainProps"

    @builtins.property
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        '''A string that specifies the name of the requested domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-domainname
        '''
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[builtins.str]:
        '''The key used to encrypt the domain.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-encryptionkey
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="permissionsPolicyDocument")
    def permissions_policy_document(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]]:
        '''The document that defines the resource policy that is set on a domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-permissionspolicydocument
        '''
        return typing.cast(typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]], jsii.get(self, "permissionsPolicyDocument"))

    @builtins.property
    @jsii.member(jsii_name="repositories")
    def repositories(self) -> typing.Optional[typing.List["IDomainRepositoryProps"]]:
        '''a list of Repositories to create.'''
        return typing.cast(typing.Optional[typing.List["IDomainRepositoryProps"]], jsii.get(self, "repositories"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''A list of tags to be applied to the domain.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-domain.html#cfn-codeartifact-domain-tags
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], jsii.get(self, "tags"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomainProps).__jsii_proxy_class__ = lambda : _IDomainPropsProxy


@jsii.interface(jsii_type="cdk-codeartifact.IDomainRepositoryProps")
class IDomainRepositoryProps(typing_extensions.Protocol):
    '''Prop definition for DomainRepository - when creating Domain and Repository together using the combined Domain construct.'''

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of an upstream repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-repositoryname
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''A text description of the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-description
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''The 12-digit account number of the AWS account that owns the domain that contains the repository.

        It does not include dashes or spaces.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-domainowner
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="externalConnections")
    def external_connections(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of external connections associated with the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-externalconnections
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="permissionsPolicyDocument")
    def permissions_policy_document(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]]:
        '''The document that defines the resource policy that is set on a repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-permissionspolicydocument
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''A list of tags to be applied to the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-tags
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="upstreams")
    def upstreams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of upstream repositories to associate with the repository.

        The order of the upstream repositories in the list determines their priority order when AWS CodeArtifact looks for a requested package version. For more information, see `Working with upstream repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-upstreams
        '''
        ...


class _IDomainRepositoryPropsProxy:
    '''Prop definition for DomainRepository - when creating Domain and Repository together using the combined Domain construct.'''

    __jsii_type__: typing.ClassVar[str] = "cdk-codeartifact.IDomainRepositoryProps"

    @builtins.property
    @jsii.member(jsii_name="repositoryName")
    def repository_name(self) -> builtins.str:
        '''The name of an upstream repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-repositoryname
        '''
        return typing.cast(builtins.str, jsii.get(self, "repositoryName"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''A text description of the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-description
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="domainOwner")
    def domain_owner(self) -> typing.Optional[builtins.str]:
        '''The 12-digit account number of the AWS account that owns the domain that contains the repository.

        It does not include dashes or spaces.

        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-domainowner
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainOwner"))

    @builtins.property
    @jsii.member(jsii_name="externalConnections")
    def external_connections(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of external connections associated with the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-externalconnections
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "externalConnections"))

    @builtins.property
    @jsii.member(jsii_name="permissionsPolicyDocument")
    def permissions_policy_document(
        self,
    ) -> typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]]:
        '''The document that defines the resource policy that is set on a repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-permissionspolicydocument
        '''
        return typing.cast(typing.Optional[typing.Union[typing.Mapping[typing.Any, typing.Any], _aws_cdk_ceddda9d.IResolvable]], jsii.get(self, "permissionsPolicyDocument"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]]:
        '''A list of tags to be applied to the repository.

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-tags
        '''
        return typing.cast(typing.Optional[typing.List[_aws_cdk_ceddda9d.CfnTag]], jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="upstreams")
    def upstreams(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of upstream repositories to associate with the repository.

        The order of the upstream repositories in the list determines their priority order when AWS CodeArtifact looks for a requested package version. For more information, see `Working with upstream repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html>`_ .

        :link: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-codeartifact-repository.html#cfn-codeartifact-repository-upstreams
        '''
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "upstreams"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IDomainRepositoryProps).__jsii_proxy_class__ = lambda : _IDomainRepositoryPropsProxy


class Repository(
    _aws_cdk_aws_codeartifact_ceddda9d.CfnRepository,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-codeartifact.Repository",
):
    '''CodeArtifact Repository Construct - extends the CfnRepository L1 construct to maintain logical naming within this library.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        domain_name: builtins.str,
        repository_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        domain_owner: typing.Optional[builtins.str] = None,
        external_connections: typing.Optional[typing.Sequence[builtins.str]] = None,
        permissions_policy_document: typing.Any = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        upstreams: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param domain_name: The name of the domain that contains the repository.
        :param repository_name: The name of an upstream repository.
        :param description: A text description of the repository.
        :param domain_owner: The 12-digit account number of the AWS account that owns the domain that contains the repository. It does not include dashes or spaces.
        :param external_connections: An array of external connections associated with the repository. For more information, see `Supported external connection repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/external-connection.html#supported-public-repositories>`_ in the *CodeArtifact user guide* .
        :param permissions_policy_document: The document that defines the resource policy that is set on a repository.
        :param tags: A list of tags to be applied to the repository.
        :param upstreams: A list of upstream repositories to associate with the repository. The order of the upstream repositories in the list determines their priority order when AWS CodeArtifact looks for a requested package version. For more information, see `Working with upstream repositories <https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html>`_ .
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ee573dc76bc92a12e354645f16bbb841f2b98ecbfd3955fb5a5fc536abfaae4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_codeartifact_ceddda9d.CfnRepositoryProps(
            domain_name=domain_name,
            repository_name=repository_name,
            description=description,
            domain_owner=domain_owner,
            external_connections=external_connections,
            permissions_policy_document=permissions_policy_document,
            tags=tags,
            upstreams=upstreams,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "CodeArtifact",
    "Domain",
    "ExternalRepository",
    "IDomainProps",
    "IDomainRepositoryProps",
    "Repository",
]

publication.publish()

def _typecheckingstub__8ba4129b8f188f7b076e9e7ac3139b96bb35845c70146fb34605d476775a4356(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IDomainProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9d581239482c4af782583fa3746f835e6fcd25dcf04f9291d316b608712285e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    props: IDomainProps,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ee573dc76bc92a12e354645f16bbb841f2b98ecbfd3955fb5a5fc536abfaae4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    domain_name: builtins.str,
    repository_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    domain_owner: typing.Optional[builtins.str] = None,
    external_connections: typing.Optional[typing.Sequence[builtins.str]] = None,
    permissions_policy_document: typing.Any = None,
    tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
    upstreams: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

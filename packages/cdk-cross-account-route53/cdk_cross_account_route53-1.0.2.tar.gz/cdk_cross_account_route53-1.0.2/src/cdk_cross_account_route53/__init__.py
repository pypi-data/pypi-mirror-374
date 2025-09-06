r'''
# AWS CDK Cross Account Route53

AWS [CDK](https://aws.amazon.com/cdk/) Constructs that define:

* IAM role that can be used to allow discrete Route53 Record changes
* Cross Account Record construct to create Route53 cross account Route53 records

These constructs allow you to create Route53 records where the zone exists in a separate AWS account to the Cloudformation Stack.

## Getting started

```shell
yarn add cdk-cross-account-route53
```

First create the role in the stack for the AWS account which contains the hosted zone.

```python
// DNS Stack
const zone = new route53.PublicHostedZone(this, 'HostedZone', {
  zoneName: 'example.com',
});

new CrossAccountRoute53Role(this, 'WebRoute53Role', {
  roleName: 'WebRoute53Role',
  assumedBy: new iam.AccountPrincipal('22222222'), // Web Stack Account
  zone,
  records: [{ domainNames: 'www.example.com' }],
 });
```

Then in the child stack create the records

```python
const hostedZoneId = 'Z12345'; // ID of the zone in the other account

const distribution = new cloudfront.Distribution(this, 'Distribution', {
  domainNames: ['example.com'],
});

new CrossAccountRoute53RecordSet(this, 'ARecord', {
  delegationRoleName: 'WebRoute53Role',
  delegationRoleAccount: '111111111', // The account that contains the zone and role
  hostedZoneId,
  resourceRecordSets: [{
    Name: `example.com`,
    Type: 'A',
    AliasTarget: {
      DNSName: distribution.distributionDomainName,
      HostedZoneId: 'Z2FDTNDATAQYW2', // Cloudfront Hosted Zone Id
      EvaluateTargetHealth: false,
    },
  }],
});
```

If you want to use wildcard matching on domains you can choose to not autonormalise the domains and pass in a wildcard e.g.

```python
new CrossAccountRoute53Role(this, 'WebRoute53Role', {
  roleName: 'WebRoute53Role',
  assumedBy: new iam.AccountPrincipal('22222222'), // Web Stack Account
  zone,
  records: [{ domainNames: '*.example.com' }],
  normaliseDomains: false,
 });
```

## CrossAccountRoute53Role

### Initializer

```python
new CrossAccountRoute53Role(scope: Construct, id: string, props: CrossAccountRoute53RoleProps)
```

*Parameters*

* **scope** Construct
* **id** string
* **props** CrossAccountRoute53RoleProps

### Construct Props

| Name             | Type                                   | Description |
| ----             | ----                                   | ----------- |
| roleName         | `string`                               | The role name |
| assumedBy        | `iam.IPrincipal`                       | The principals that are allowed to assume the role |
| zone             | `route53.IHostedZone`                  | The hosted zone. |
| records          | `CrossAccountRoute53RolePropsRecord[]` | The records that can be created by this role |
| normaliseDomains | `boolean`                              | Normalise the domains names as per AWS documentation (default: true) |

### CrossAccountRoute53RolePropsRecords

| Name        | Type                               | Description |
| ----        | ----                               | ----------- |
| domainNames | `string \| string[]`               | The names of the records that can be created or changed |
| types       | `route53.RecordType[]`             | The typepsof records that can be created. Default `['A', 'AAAA']` |
| actions     | `'CREATE' \| 'UPSERT' \| 'DELETE'` | The allowed actions. Default `['CREATE', 'UPSERT', 'DELETE']` |

## CrossAccountRoute53RecordSet

### Initializer

```python
new CrossAccountRoute53RecordSet(scope: Construct, id: string, props: CrossAccountRoute53RecordSetProps)
```

*Parameters*

* **scope** Construct
* **id** string
* **props** CrossAccountRoute53RecordSet

### Construct Props

| Name        | Type                                   | Description |
| ----        | ----                                   | ----------- |
| delegationRoleName    | `string`                     | The role name created in the account with the hosted zone |
| delegationRoleAccount | `string`                     | The account identfier of the account with the hosted zone |
| hostedZoneId          | `string`                     | The hosted zoned id |
| resourceRecordSets    | `Route53.ResourceRecordSets` | The changes to be applied. These are in the same format as taken by [ChangeResourceRecordSets Action](https://docs.aws.amazon.com/Route53/latest/APIReference/API_ResourceRecordSet.html) |

## Development Status

These constructs will stay in `v0.x.x` for a while, to allow easier bug fixing & breaking changes *if absolutely needed*.
Once bugs are fixed (if any), the constructs will be published with `v1` major version and will be marked as stable.

Only typescript has been tested.

## Development

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
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

import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_route53 as _aws_cdk_aws_route53_ceddda9d
import constructs as _constructs_77d1e7e8


class CrossAccountRoute53RecordSet(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cross-account-route53.CrossAccountRoute53RecordSet",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        delegation_role_account: builtins.str,
        delegation_role_name: builtins.str,
        hosted_zone_id: builtins.str,
        resource_record_sets: typing.Any,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param delegation_role_account: 
        :param delegation_role_name: 
        :param hosted_zone_id: 
        :param resource_record_sets: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb9cea0214e8012c1e31d0b1d7d6035056485aca5f92308e657887745b362b15)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrossAccountRoute53RecordSetProps(
            delegation_role_account=delegation_role_account,
            delegation_role_name=delegation_role_name,
            hosted_zone_id=hosted_zone_id,
            resource_record_sets=resource_record_sets,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-cross-account-route53.CrossAccountRoute53RecordSetProps",
    jsii_struct_bases=[],
    name_mapping={
        "delegation_role_account": "delegationRoleAccount",
        "delegation_role_name": "delegationRoleName",
        "hosted_zone_id": "hostedZoneId",
        "resource_record_sets": "resourceRecordSets",
    },
)
class CrossAccountRoute53RecordSetProps:
    def __init__(
        self,
        *,
        delegation_role_account: builtins.str,
        delegation_role_name: builtins.str,
        hosted_zone_id: builtins.str,
        resource_record_sets: typing.Any,
    ) -> None:
        '''
        :param delegation_role_account: 
        :param delegation_role_name: 
        :param hosted_zone_id: 
        :param resource_record_sets: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cac8f19d83c5f24cbf4bce04fa317b53b93763df35ea46a76e0388b04dbbf8b)
            check_type(argname="argument delegation_role_account", value=delegation_role_account, expected_type=type_hints["delegation_role_account"])
            check_type(argname="argument delegation_role_name", value=delegation_role_name, expected_type=type_hints["delegation_role_name"])
            check_type(argname="argument hosted_zone_id", value=hosted_zone_id, expected_type=type_hints["hosted_zone_id"])
            check_type(argname="argument resource_record_sets", value=resource_record_sets, expected_type=type_hints["resource_record_sets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "delegation_role_account": delegation_role_account,
            "delegation_role_name": delegation_role_name,
            "hosted_zone_id": hosted_zone_id,
            "resource_record_sets": resource_record_sets,
        }

    @builtins.property
    def delegation_role_account(self) -> builtins.str:
        result = self._values.get("delegation_role_account")
        assert result is not None, "Required property 'delegation_role_account' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delegation_role_name(self) -> builtins.str:
        result = self._values.get("delegation_role_name")
        assert result is not None, "Required property 'delegation_role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hosted_zone_id(self) -> builtins.str:
        result = self._values.get("hosted_zone_id")
        assert result is not None, "Required property 'hosted_zone_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_record_sets(self) -> typing.Any:
        result = self._values.get("resource_record_sets")
        assert result is not None, "Required property 'resource_record_sets' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountRoute53RecordSetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CrossAccountRoute53Role(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-cross-account-route53.CrossAccountRoute53Role",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        assumed_by: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
        records: typing.Sequence[typing.Union["CrossAccountRoute53RolePropsRecord", typing.Dict[builtins.str, typing.Any]]],
        role_name: builtins.str,
        zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        normalise_domains: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param assumed_by: 
        :param records: 
        :param role_name: 
        :param zone: 
        :param normalise_domains: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2777059880dc724db574f149bd93852749be71b9a03bfd12a8b2831bea2f1ad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CrossAccountRoute53RoleProps(
            assumed_by=assumed_by,
            records=records,
            role_name=role_name,
            zone=zone,
            normalise_domains=normalise_domains,
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-cross-account-route53.CrossAccountRoute53RoleProps",
    jsii_struct_bases=[],
    name_mapping={
        "assumed_by": "assumedBy",
        "records": "records",
        "role_name": "roleName",
        "zone": "zone",
        "normalise_domains": "normaliseDomains",
    },
)
class CrossAccountRoute53RoleProps:
    def __init__(
        self,
        *,
        assumed_by: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
        records: typing.Sequence[typing.Union["CrossAccountRoute53RolePropsRecord", typing.Dict[builtins.str, typing.Any]]],
        role_name: builtins.str,
        zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
        normalise_domains: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param assumed_by: 
        :param records: 
        :param role_name: 
        :param zone: 
        :param normalise_domains: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aab09315b12b751f1bd405aadc611cb8fb81dcba8f4bb3504d50f884bdd9e42b)
            check_type(argname="argument assumed_by", value=assumed_by, expected_type=type_hints["assumed_by"])
            check_type(argname="argument records", value=records, expected_type=type_hints["records"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
            check_type(argname="argument normalise_domains", value=normalise_domains, expected_type=type_hints["normalise_domains"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "assumed_by": assumed_by,
            "records": records,
            "role_name": role_name,
            "zone": zone,
        }
        if normalise_domains is not None:
            self._values["normalise_domains"] = normalise_domains

    @builtins.property
    def assumed_by(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        result = self._values.get("assumed_by")
        assert result is not None, "Required property 'assumed_by' is missing"
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, result)

    @builtins.property
    def records(self) -> typing.List["CrossAccountRoute53RolePropsRecord"]:
        result = self._values.get("records")
        assert result is not None, "Required property 'records' is missing"
        return typing.cast(typing.List["CrossAccountRoute53RolePropsRecord"], result)

    @builtins.property
    def role_name(self) -> builtins.str:
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def zone(self) -> _aws_cdk_aws_route53_ceddda9d.IHostedZone:
        result = self._values.get("zone")
        assert result is not None, "Required property 'zone' is missing"
        return typing.cast(_aws_cdk_aws_route53_ceddda9d.IHostedZone, result)

    @builtins.property
    def normalise_domains(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("normalise_domains")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountRoute53RoleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-cross-account-route53.CrossAccountRoute53RolePropsRecord",
    jsii_struct_bases=[],
    name_mapping={
        "domain_names": "domainNames",
        "actions": "actions",
        "types": "types",
    },
)
class CrossAccountRoute53RolePropsRecord:
    def __init__(
        self,
        *,
        domain_names: typing.Union[builtins.str, typing.Sequence[builtins.str]],
        actions: typing.Optional[typing.Sequence[builtins.str]] = None,
        types: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param domain_names: 
        :param actions: 
        :param types: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b699bfb7ef370c698d3a68a56a5765e23d7c3f538fb1527d92400fe46b2e20b)
            check_type(argname="argument domain_names", value=domain_names, expected_type=type_hints["domain_names"])
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument types", value=types, expected_type=type_hints["types"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_names": domain_names,
        }
        if actions is not None:
            self._values["actions"] = actions
        if types is not None:
            self._values["types"] = types

    @builtins.property
    def domain_names(self) -> typing.Union[builtins.str, typing.List[builtins.str]]:
        result = self._values.get("domain_names")
        assert result is not None, "Required property 'domain_names' is missing"
        return typing.cast(typing.Union[builtins.str, typing.List[builtins.str]], result)

    @builtins.property
    def actions(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("actions")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def types(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CrossAccountRoute53RolePropsRecord(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CrossAccountRoute53RecordSet",
    "CrossAccountRoute53RecordSetProps",
    "CrossAccountRoute53Role",
    "CrossAccountRoute53RoleProps",
    "CrossAccountRoute53RolePropsRecord",
]

publication.publish()

def _typecheckingstub__eb9cea0214e8012c1e31d0b1d7d6035056485aca5f92308e657887745b362b15(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    delegation_role_account: builtins.str,
    delegation_role_name: builtins.str,
    hosted_zone_id: builtins.str,
    resource_record_sets: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cac8f19d83c5f24cbf4bce04fa317b53b93763df35ea46a76e0388b04dbbf8b(
    *,
    delegation_role_account: builtins.str,
    delegation_role_name: builtins.str,
    hosted_zone_id: builtins.str,
    resource_record_sets: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2777059880dc724db574f149bd93852749be71b9a03bfd12a8b2831bea2f1ad(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    assumed_by: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    records: typing.Sequence[typing.Union[CrossAccountRoute53RolePropsRecord, typing.Dict[builtins.str, typing.Any]]],
    role_name: builtins.str,
    zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    normalise_domains: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab09315b12b751f1bd405aadc611cb8fb81dcba8f4bb3504d50f884bdd9e42b(
    *,
    assumed_by: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
    records: typing.Sequence[typing.Union[CrossAccountRoute53RolePropsRecord, typing.Dict[builtins.str, typing.Any]]],
    role_name: builtins.str,
    zone: _aws_cdk_aws_route53_ceddda9d.IHostedZone,
    normalise_domains: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b699bfb7ef370c698d3a68a56a5765e23d7c3f538fb1527d92400fe46b2e20b(
    *,
    domain_names: typing.Union[builtins.str, typing.Sequence[builtins.str]],
    actions: typing.Optional[typing.Sequence[builtins.str]] = None,
    types: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

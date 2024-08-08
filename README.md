# ConfigCat OpenFeature Provider for Python

[![CI](https://github.com/configcat/openfeature-python/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/configcat/openfeature-python/actions/workflows/ci.yml) 
[![PyPI](https://img.shields.io/pypi/v/configcat-openfeature-provider.svg)](https://pypi.python.org/pypi/configcat-openfeature-provider)
[![PyPI](https://img.shields.io/pypi/pyversions/configcat-openfeature-provider.svg)](https://pypi.python.org/pypi/configcat-openfeature-provider)

This repository contains an OpenFeature provider that allows [ConfigCat](https://configcat.com) to be used with the [OpenFeature Python SDK](https://github.com/open-feature/python-sdk).

## Installation

```sh
pip install configcat-openfeature-provider
```

## Usage

The `ConfigCatProvider` constructor takes the SDK key and an optional `ConfigCatOptions` argument containing the additional configuration options for the [ConfigCat Python SDK](https://github.com/configcat/python-sdk):

```python
from configcatclient import ConfigCatOptions, PollingMode
from openfeature import api
from configcat_openfeature_provider import ConfigCatProvider

# Configure the OpenFeature API with the ConfigCat provider.
api.set_provider(
    ConfigCatProvider(
        "<YOUR-CONFIGCAT-SDK-KEY>",
        # Configure the ConfigCat SDK.
        ConfigCatOptions(
            polling_mode=PollingMode.auto_poll(60),
        ),
    )
)

# Create a client.
client = api.get_client()

# Evaluate a feature flag.
is_awesome_feature_enabled = client.get_boolean_value("isAwesomeFeatureEnabled", False)
```

For more information about all the configuration options, see the [Python SDK documentation](https://configcat.com/docs/sdk-reference/python/#creating-the-configcat-client).

## Need help?
https://configcat.com/support

## Contributing
Contributions are welcome. For more info please read the [Contribution Guideline](CONTRIBUTING.md).

## About ConfigCat
ConfigCat is a feature flag and configuration management service that lets you separate releases from deployments. You can turn your features ON/OFF using <a href="https://app.configcat.com" target="_blank">ConfigCat Dashboard</a> even after they are deployed. ConfigCat lets you target specific groups of users based on region, email or any other custom user attribute.

ConfigCat is a <a href="https://configcat.com" target="_blank">hosted feature flag service</a>. Manage feature toggles across frontend, backend, mobile, desktop apps. <a href="https://configcat.com" target="_blank">Alternative to LaunchDarkly</a>. Management app + feature flag SDKs.

- [Official ConfigCat SDKs for other platforms](https://github.com/configcat)
- [Documentation](https://configcat.com/docs)
- [Blog](https://configcat.com/blog)

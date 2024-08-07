from os import path

import pytest

from configcatclient import ConfigCatOptions, PollingMode
from configcatclient.localfiledatasource import LocalFileFlagOverrides
from configcatclient.overridedatasource import OverrideBehaviour
from openfeature import api
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ErrorCode
from openfeature.flag_evaluation import Reason

from configcat_openfeature_provider import ConfigCatProvider


@pytest.fixture
def provider_client():
    api.set_provider(
        ConfigCatProvider(
            "local",
            ConfigCatOptions(
                flag_overrides=LocalFileFlagOverrides(
                    file_path=path.join(
                        path.dirname(__file__), "data/test_json_complex.json"
                    ),
                    override_behaviour=OverrideBehaviour.LocalOnly,
                ),
                polling_mode=PollingMode.auto_poll(60),
            ),
        )
    )
    return api.get_client()


def test_metadata(provider_client):
    assert provider_client.provider.get_metadata().name == "ConfigCatProvider"


def test_eval_bool(provider_client):
    details = provider_client.get_boolean_details("enabledFeature", False)

    assert details.value is True
    assert details.variant == "v-enabled"
    assert details.reason == Reason.DEFAULT


def test_eval_int(provider_client):
    details = provider_client.get_integer_details("intSetting", 0)

    assert details.value == 5
    assert details.variant == "v-int"
    assert details.reason == Reason.DEFAULT


def test_eval_float(provider_client):
    details = provider_client.get_float_details("doubleSetting", 0.0)

    assert details.value == 1.2
    assert details.variant == "v-double"
    assert details.reason == Reason.DEFAULT


def test_eval_str(provider_client):
    details = provider_client.get_string_details("stringSetting", "")

    assert details.value == "test"
    assert details.variant == "v-string"
    assert details.reason == Reason.DEFAULT


def test_eval_object(provider_client):
    details = provider_client.get_object_details("objectSetting", {})

    assert details.value == {"bool_field": True, "text_field": "value"}
    assert details.variant == "v-object"
    assert details.reason == Reason.DEFAULT


def test_eval_targeting(provider_client):
    ctx = EvaluationContext(targeting_key="example@matching.com")
    details = provider_client.get_boolean_details("disabledFeature", False, ctx)

    assert details.value is True
    assert details.variant == "v-disabled-t"
    assert details.reason == Reason.TARGETING_MATCH


def test_eval_key_not_found(provider_client):
    details = provider_client.get_boolean_details("non-existing", False)

    assert details.error_code == ErrorCode.FLAG_NOT_FOUND
    assert (
        "Failed to evaluate setting 'non-existing' (the key was not found in config JSON)"
        in details.error_message
    )
    assert details.reason == Reason.ERROR


def test_eval_type_mismatch(provider_client):
    details = provider_client.get_boolean_details("stringSetting", False)

    assert details.error_code == ErrorCode.TYPE_MISMATCH
    assert details.reason == Reason.ERROR

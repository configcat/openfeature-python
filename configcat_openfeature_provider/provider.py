import json
import typing

from configcatclient import ConfigCatClient, ConfigCatOptions
from configcatclient.evaluationdetails import EvaluationDetails
from configcatclient.user import User
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ErrorCode
from openfeature.flag_evaluation import FlagResolutionDetails, Reason
from openfeature.provider import AbstractProvider, Metadata


class ConfigCatProvider(AbstractProvider):
    def __init__(self, sdk_key: str, options: typing.Optional[ConfigCatOptions] = None):
        self.client = ConfigCatClient.get(sdk_key, options)

    def get_metadata(self) -> Metadata:
        return Metadata("ConfigCatProvider")

    def shutdown(self) -> None:
        self.client.close()

    def resolve_boolean_details(
        self,
        flag_key: str,
        default_value: bool,
        evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        user = self.__ctx_to_user(evaluation_context)
        details = self.client.get_value_details(flag_key, default_value, user)

        if not isinstance(details.value, bool):
            return self.__mismatched_type(default_value)

        return self.__produce_result(details, default_value)

    def resolve_string_details(
        self,
        flag_key: str,
        default_value: str,
        evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        user = self.__ctx_to_user(evaluation_context)
        details = self.client.get_value_details(flag_key, default_value, user)

        if not isinstance(details.value, str):
            return self.__mismatched_type(default_value)

        return self.__produce_result(details, default_value)

    def resolve_integer_details(
        self,
        flag_key: str,
        default_value: int,
        evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        user = self.__ctx_to_user(evaluation_context)
        details = self.client.get_value_details(flag_key, default_value, user)

        if not isinstance(details.value, int):
            return self.__mismatched_type(default_value)

        return self.__produce_result(details, default_value)

    def resolve_float_details(
        self,
        flag_key: str,
        default_value: float,
        evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        user = self.__ctx_to_user(evaluation_context)
        details = self.client.get_value_details(flag_key, default_value, user)

        if not isinstance(details.value, float):
            return self.__mismatched_type(default_value)

        return self.__produce_result(details, default_value)

    def resolve_object_details(
        self,
        flag_key: str,
        default_value: typing.Union[dict, list],
        evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[typing.Union[dict, list]]:
        user = self.__ctx_to_user(evaluation_context)
        details = self.client.get_value_details(flag_key, "", user)

        if not isinstance(details.value, str):
            return self.__mismatched_type(default_value)

        try:
            return FlagResolutionDetails(
                value=json.loads(details.value),
                variant=details.variation_id,
                reason=Reason(self.__produce_reason(details)),
            )
        except json.JSONDecodeError as e:
            return FlagResolutionDetails(
                value=default_value,
                reason=Reason(Reason.ERROR),
                error_message=e.msg,
                error_code=ErrorCode.TYPE_MISMATCH,
            )

    def __produce_result(
        self,
        details: EvaluationDetails,
        default_value: typing.Any,
    ) -> FlagResolutionDetails:
        if details.error is not None:
            err_code = (
                ErrorCode.FLAG_NOT_FOUND
                if "key was not found in config JSON" in details.error
                else ErrorCode.GENERAL
            )
            return FlagResolutionDetails(
                value=default_value,
                reason=Reason(Reason.ERROR),
                error_message=details.error,
                error_code=err_code,
            )

        return FlagResolutionDetails(
            value=details.value,
            variant=details.variation_id,
            reason=Reason(self.__produce_reason(details)),
        )

    @staticmethod
    def __ctx_to_user(ctx: typing.Optional[EvaluationContext]) -> typing.Optional[User]:
        if ctx is None or (not ctx.targeting_key and not ctx.attributes):
            return None

        email = ctx.attributes.get("Email")
        country = ctx.attributes.get("Country")
        return User(ctx.targeting_key, email, country, ctx.attributes)

    @staticmethod
    def __mismatched_type(default_value: typing.Any) -> FlagResolutionDetails:
        return FlagResolutionDetails(
            value=default_value,
            reason=Reason(Reason.ERROR),
            error_code=ErrorCode.TYPE_MISMATCH,
        )

    @staticmethod
    def __produce_reason(details: EvaluationDetails) -> str:
        if details.error is not None:
            return Reason.ERROR

        if (
            details.matched_targeting_rule is not None
            or details.matched_percentage_option is not None
        ):
            return Reason.TARGETING_MATCH

        return Reason.DEFAULT

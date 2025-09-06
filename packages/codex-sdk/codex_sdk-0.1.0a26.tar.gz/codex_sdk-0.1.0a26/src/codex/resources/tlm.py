# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..types import tlm_score_params, tlm_prompt_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, SequenceNotStr
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.tlm_score_response import TlmScoreResponse
from ..types.tlm_prompt_response import TlmPromptResponse

__all__ = ["TlmResource", "AsyncTlmResource"]


class TlmResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TlmResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/cleanlab/codex-python#accessing-raw-response-data-eg-headers
        """
        return TlmResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TlmResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/cleanlab/codex-python#with_streaming_response
        """
        return TlmResourceWithStreamingResponse(self)

    def prompt(
        self,
        *,
        prompt: str,
        constrain_outputs: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        options: Optional[tlm_prompt_params.Options] | NotGiven = NOT_GIVEN,
        quality_preset: Literal["best", "high", "medium", "low", "base"] | NotGiven = NOT_GIVEN,
        task: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TlmPromptResponse:
        """
        Prompts the TLM API.

        Args:
          options: Typed dict of advanced configuration options for the Trustworthy Language Model.
              Many of these configurations are determined by the quality preset selected
              (learn about quality presets in the TLM [initialization method](./#class-tlm)).
              Specifying TLMOptions values directly overrides any default values set from the
              quality preset.

              For all options described below, higher settings will lead to longer runtimes
              and may consume more tokens internally. You may not be able to run long prompts
              (or prompts with long responses) in your account, unless your token/rate limits
              are increased. If you hit token limit issues, try lower/less expensive
              TLMOptions to be able to run longer prompts/responses, or contact Cleanlab to
              increase your limits.

              The default values corresponding to each quality preset are:

              - **best:** `num_consistency_samples` = 8, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **high:** `num_consistency_samples` = 4, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **medium:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **low:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"none"`.
              - **base:** `num_consistency_samples` = 0, `num_self_reflections` = 1,
                `reasoning_effort` = `"none"`.

              By default, TLM uses the: "medium" `quality_preset`, "gpt-4.1-mini" base
              `model`, and `max_tokens` is set to 512. You can set custom values for these
              arguments regardless of the quality preset specified.

              Args: model ({"gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini",
              "gpt-4.1-nano", "o4-mini", "o3", "gpt-4.5-preview", "gpt-4o-mini", "gpt-4o",
              "o3-mini", "o1", "o1-mini", "gpt-4", "gpt-3.5-turbo-16k", "claude-opus-4-0",
              "claude-sonnet-4-0", "claude-3.7-sonnet", "claude-3.5-sonnet-v2",
              "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-haiku", "nova-micro",
              "nova-lite", "nova-pro"}, default = "gpt-4.1-mini"): Underlying base LLM to use
              (better models yield better results, faster models yield faster results). -
              Models still in beta: "o3", "o1", "o4-mini", "o3-mini", "o1-mini",
              "gpt-4.5-preview", "claude-opus-4-0", "claude-sonnet-4-0", "claude-3.7-sonnet",
              "claude-3.5-haiku". - Recommended models for accuracy: "gpt-5", "gpt-4.1",
              "o4-mini", "o3", "claude-opus-4-0", "claude-sonnet-4-0". - Recommended models
              for low latency/costs: "gpt-4.1-nano", "nova-micro".

                  log (list[str], default = []): optionally specify additional logs or metadata that TLM should return.
                  For instance, include "explanation" here to get explanations of why a response is scored with low trustworthiness.

                  custom_eval_criteria (list[dict[str, Any]], default = []): optionally specify custom evalution criteria beyond the built-in trustworthiness scoring.
                  The expected input format is a list of dictionaries, where each dictionary has the following keys:
                  - name: Name of the evaluation criteria.
                  - criteria: Instructions specifying the evaluation criteria.

                  max_tokens (int, default = 512): the maximum number of tokens that can be generated in the response from `TLM.prompt()` as well as during internal trustworthiness scoring.
                  If you experience token/rate-limit errors, try lowering this number.
                  For OpenAI models, this parameter must be between 64 and 4096. For Claude models, this parameter must be between 64 and 512.

                  reasoning_effort ({"none", "low", "medium", "high"}, default = "high"): how much internal LLM calls are allowed to reason (number of thinking tokens)
                  when generating alternative possible responses and reflecting on responses during trustworthiness scoring.
                  Reduce this value to reduce runtimes. Higher values may improve trust scoring.

                  num_self_reflections (int, default = 3): the number of different evaluations to perform where the LLM reflects on the response, a factor affecting trust scoring.
                  The maximum number currently supported is 3. Lower values can reduce runtimes.
                  Reflection helps quantify aleatoric uncertainty associated with challenging prompts and catches responses that are noticeably incorrect/bad upon further analysis.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  num_consistency_samples (int, default = 8): the amount of internal sampling to measure LLM response consistency, a factor affecting trust scoring.
                  Must be between 0 and 20. Lower values can reduce runtimes.
                  Measuring consistency helps quantify the epistemic uncertainty associated with
                  strange prompts or prompts that are too vague/open-ended to receive a clearly defined 'good' response.
                  TLM measures consistency via the degree of contradiction between sampled responses that the model considers plausible.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  similarity_measure ({"semantic", "string", "embedding", "embedding_large", "code", "discrepancy"}, default = "discrepancy"): how the
                  trustworthiness scoring's consistency algorithm measures similarity between alternative responses considered plausible by the model.
                  Supported similarity measures include - "semantic" (based on natural language inference),
                  "embedding" (based on vector embedding similarity), "embedding_large" (based on a larger embedding model),
                  "code" (based on model-based analysis designed to compare code), "discrepancy" (based on model-based analysis of possible discrepancies),
                  and "string" (based on character/word overlap). Set this to "string" for minimal runtimes.
                  This parameter has no effect when `num_consistency_samples = 0`.

                  num_candidate_responses (int, default = 1): how many alternative candidate responses are internally generated in `TLM.prompt()`.
                  `TLM.prompt()` scores the trustworthiness of each candidate response, and then returns the most trustworthy one.
                  You can auto-improve responses by increasing this parameter, but at higher runtimes/costs.
                  This parameter must be between 1 and 20. It has no effect on `TLM.score()`.
                  When this parameter is 1, `TLM.prompt()` simply returns a standard LLM response and does not attempt to auto-improve it.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  disable_trustworthiness (bool, default = False): if True, trustworthiness scoring is disabled and TLM will not compute trust scores for responses.
                  This is useful when you only want to use custom evaluation criteria or when you want to minimize computational overhead and only need the base LLM response.
                  The following parameters will be ignored when `disable_trustworthiness` is True: `num_consistency_samples`, `num_self_reflections`, `num_candidate_responses`, `reasoning_effort`, `similarity_measure`.

          quality_preset: The quality preset to use for the TLM or Trustworthy RAG API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/tlm/prompt",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "constrain_outputs": constrain_outputs,
                    "options": options,
                    "quality_preset": quality_preset,
                    "task": task,
                },
                tlm_prompt_params.TlmPromptParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TlmPromptResponse,
        )

    def score(
        self,
        *,
        prompt: str,
        response: str,
        constrain_outputs: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        options: Optional[tlm_score_params.Options] | NotGiven = NOT_GIVEN,
        quality_preset: Literal["best", "high", "medium", "low", "base"] | NotGiven = NOT_GIVEN,
        task: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TlmScoreResponse:
        """
        Scores the TLM API.

        TODO:

        - Track query count in DB
        - Enforce hard cap on queries for users w/o credit card on file

        Args:
          options: Typed dict of advanced configuration options for the Trustworthy Language Model.
              Many of these configurations are determined by the quality preset selected
              (learn about quality presets in the TLM [initialization method](./#class-tlm)).
              Specifying TLMOptions values directly overrides any default values set from the
              quality preset.

              For all options described below, higher settings will lead to longer runtimes
              and may consume more tokens internally. You may not be able to run long prompts
              (or prompts with long responses) in your account, unless your token/rate limits
              are increased. If you hit token limit issues, try lower/less expensive
              TLMOptions to be able to run longer prompts/responses, or contact Cleanlab to
              increase your limits.

              The default values corresponding to each quality preset are:

              - **best:** `num_consistency_samples` = 8, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **high:** `num_consistency_samples` = 4, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **medium:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **low:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"none"`.
              - **base:** `num_consistency_samples` = 0, `num_self_reflections` = 1,
                `reasoning_effort` = `"none"`.

              By default, TLM uses the: "medium" `quality_preset`, "gpt-4.1-mini" base
              `model`, and `max_tokens` is set to 512. You can set custom values for these
              arguments regardless of the quality preset specified.

              Args: model ({"gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini",
              "gpt-4.1-nano", "o4-mini", "o3", "gpt-4.5-preview", "gpt-4o-mini", "gpt-4o",
              "o3-mini", "o1", "o1-mini", "gpt-4", "gpt-3.5-turbo-16k", "claude-opus-4-0",
              "claude-sonnet-4-0", "claude-3.7-sonnet", "claude-3.5-sonnet-v2",
              "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-haiku", "nova-micro",
              "nova-lite", "nova-pro"}, default = "gpt-4.1-mini"): Underlying base LLM to use
              (better models yield better results, faster models yield faster results). -
              Models still in beta: "o3", "o1", "o4-mini", "o3-mini", "o1-mini",
              "gpt-4.5-preview", "claude-opus-4-0", "claude-sonnet-4-0", "claude-3.7-sonnet",
              "claude-3.5-haiku". - Recommended models for accuracy: "gpt-5", "gpt-4.1",
              "o4-mini", "o3", "claude-opus-4-0", "claude-sonnet-4-0". - Recommended models
              for low latency/costs: "gpt-4.1-nano", "nova-micro".

                  log (list[str], default = []): optionally specify additional logs or metadata that TLM should return.
                  For instance, include "explanation" here to get explanations of why a response is scored with low trustworthiness.

                  custom_eval_criteria (list[dict[str, Any]], default = []): optionally specify custom evalution criteria beyond the built-in trustworthiness scoring.
                  The expected input format is a list of dictionaries, where each dictionary has the following keys:
                  - name: Name of the evaluation criteria.
                  - criteria: Instructions specifying the evaluation criteria.

                  max_tokens (int, default = 512): the maximum number of tokens that can be generated in the response from `TLM.prompt()` as well as during internal trustworthiness scoring.
                  If you experience token/rate-limit errors, try lowering this number.
                  For OpenAI models, this parameter must be between 64 and 4096. For Claude models, this parameter must be between 64 and 512.

                  reasoning_effort ({"none", "low", "medium", "high"}, default = "high"): how much internal LLM calls are allowed to reason (number of thinking tokens)
                  when generating alternative possible responses and reflecting on responses during trustworthiness scoring.
                  Reduce this value to reduce runtimes. Higher values may improve trust scoring.

                  num_self_reflections (int, default = 3): the number of different evaluations to perform where the LLM reflects on the response, a factor affecting trust scoring.
                  The maximum number currently supported is 3. Lower values can reduce runtimes.
                  Reflection helps quantify aleatoric uncertainty associated with challenging prompts and catches responses that are noticeably incorrect/bad upon further analysis.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  num_consistency_samples (int, default = 8): the amount of internal sampling to measure LLM response consistency, a factor affecting trust scoring.
                  Must be between 0 and 20. Lower values can reduce runtimes.
                  Measuring consistency helps quantify the epistemic uncertainty associated with
                  strange prompts or prompts that are too vague/open-ended to receive a clearly defined 'good' response.
                  TLM measures consistency via the degree of contradiction between sampled responses that the model considers plausible.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  similarity_measure ({"semantic", "string", "embedding", "embedding_large", "code", "discrepancy"}, default = "discrepancy"): how the
                  trustworthiness scoring's consistency algorithm measures similarity between alternative responses considered plausible by the model.
                  Supported similarity measures include - "semantic" (based on natural language inference),
                  "embedding" (based on vector embedding similarity), "embedding_large" (based on a larger embedding model),
                  "code" (based on model-based analysis designed to compare code), "discrepancy" (based on model-based analysis of possible discrepancies),
                  and "string" (based on character/word overlap). Set this to "string" for minimal runtimes.
                  This parameter has no effect when `num_consistency_samples = 0`.

                  num_candidate_responses (int, default = 1): how many alternative candidate responses are internally generated in `TLM.prompt()`.
                  `TLM.prompt()` scores the trustworthiness of each candidate response, and then returns the most trustworthy one.
                  You can auto-improve responses by increasing this parameter, but at higher runtimes/costs.
                  This parameter must be between 1 and 20. It has no effect on `TLM.score()`.
                  When this parameter is 1, `TLM.prompt()` simply returns a standard LLM response and does not attempt to auto-improve it.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  disable_trustworthiness (bool, default = False): if True, trustworthiness scoring is disabled and TLM will not compute trust scores for responses.
                  This is useful when you only want to use custom evaluation criteria or when you want to minimize computational overhead and only need the base LLM response.
                  The following parameters will be ignored when `disable_trustworthiness` is True: `num_consistency_samples`, `num_self_reflections`, `num_candidate_responses`, `reasoning_effort`, `similarity_measure`.

          quality_preset: The quality preset to use for the TLM or Trustworthy RAG API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/tlm/score",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "response": response,
                    "constrain_outputs": constrain_outputs,
                    "options": options,
                    "quality_preset": quality_preset,
                    "task": task,
                },
                tlm_score_params.TlmScoreParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TlmScoreResponse,
        )


class AsyncTlmResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTlmResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/cleanlab/codex-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTlmResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTlmResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/cleanlab/codex-python#with_streaming_response
        """
        return AsyncTlmResourceWithStreamingResponse(self)

    async def prompt(
        self,
        *,
        prompt: str,
        constrain_outputs: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        options: Optional[tlm_prompt_params.Options] | NotGiven = NOT_GIVEN,
        quality_preset: Literal["best", "high", "medium", "low", "base"] | NotGiven = NOT_GIVEN,
        task: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TlmPromptResponse:
        """
        Prompts the TLM API.

        Args:
          options: Typed dict of advanced configuration options for the Trustworthy Language Model.
              Many of these configurations are determined by the quality preset selected
              (learn about quality presets in the TLM [initialization method](./#class-tlm)).
              Specifying TLMOptions values directly overrides any default values set from the
              quality preset.

              For all options described below, higher settings will lead to longer runtimes
              and may consume more tokens internally. You may not be able to run long prompts
              (or prompts with long responses) in your account, unless your token/rate limits
              are increased. If you hit token limit issues, try lower/less expensive
              TLMOptions to be able to run longer prompts/responses, or contact Cleanlab to
              increase your limits.

              The default values corresponding to each quality preset are:

              - **best:** `num_consistency_samples` = 8, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **high:** `num_consistency_samples` = 4, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **medium:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **low:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"none"`.
              - **base:** `num_consistency_samples` = 0, `num_self_reflections` = 1,
                `reasoning_effort` = `"none"`.

              By default, TLM uses the: "medium" `quality_preset`, "gpt-4.1-mini" base
              `model`, and `max_tokens` is set to 512. You can set custom values for these
              arguments regardless of the quality preset specified.

              Args: model ({"gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini",
              "gpt-4.1-nano", "o4-mini", "o3", "gpt-4.5-preview", "gpt-4o-mini", "gpt-4o",
              "o3-mini", "o1", "o1-mini", "gpt-4", "gpt-3.5-turbo-16k", "claude-opus-4-0",
              "claude-sonnet-4-0", "claude-3.7-sonnet", "claude-3.5-sonnet-v2",
              "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-haiku", "nova-micro",
              "nova-lite", "nova-pro"}, default = "gpt-4.1-mini"): Underlying base LLM to use
              (better models yield better results, faster models yield faster results). -
              Models still in beta: "o3", "o1", "o4-mini", "o3-mini", "o1-mini",
              "gpt-4.5-preview", "claude-opus-4-0", "claude-sonnet-4-0", "claude-3.7-sonnet",
              "claude-3.5-haiku". - Recommended models for accuracy: "gpt-5", "gpt-4.1",
              "o4-mini", "o3", "claude-opus-4-0", "claude-sonnet-4-0". - Recommended models
              for low latency/costs: "gpt-4.1-nano", "nova-micro".

                  log (list[str], default = []): optionally specify additional logs or metadata that TLM should return.
                  For instance, include "explanation" here to get explanations of why a response is scored with low trustworthiness.

                  custom_eval_criteria (list[dict[str, Any]], default = []): optionally specify custom evalution criteria beyond the built-in trustworthiness scoring.
                  The expected input format is a list of dictionaries, where each dictionary has the following keys:
                  - name: Name of the evaluation criteria.
                  - criteria: Instructions specifying the evaluation criteria.

                  max_tokens (int, default = 512): the maximum number of tokens that can be generated in the response from `TLM.prompt()` as well as during internal trustworthiness scoring.
                  If you experience token/rate-limit errors, try lowering this number.
                  For OpenAI models, this parameter must be between 64 and 4096. For Claude models, this parameter must be between 64 and 512.

                  reasoning_effort ({"none", "low", "medium", "high"}, default = "high"): how much internal LLM calls are allowed to reason (number of thinking tokens)
                  when generating alternative possible responses and reflecting on responses during trustworthiness scoring.
                  Reduce this value to reduce runtimes. Higher values may improve trust scoring.

                  num_self_reflections (int, default = 3): the number of different evaluations to perform where the LLM reflects on the response, a factor affecting trust scoring.
                  The maximum number currently supported is 3. Lower values can reduce runtimes.
                  Reflection helps quantify aleatoric uncertainty associated with challenging prompts and catches responses that are noticeably incorrect/bad upon further analysis.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  num_consistency_samples (int, default = 8): the amount of internal sampling to measure LLM response consistency, a factor affecting trust scoring.
                  Must be between 0 and 20. Lower values can reduce runtimes.
                  Measuring consistency helps quantify the epistemic uncertainty associated with
                  strange prompts or prompts that are too vague/open-ended to receive a clearly defined 'good' response.
                  TLM measures consistency via the degree of contradiction between sampled responses that the model considers plausible.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  similarity_measure ({"semantic", "string", "embedding", "embedding_large", "code", "discrepancy"}, default = "discrepancy"): how the
                  trustworthiness scoring's consistency algorithm measures similarity between alternative responses considered plausible by the model.
                  Supported similarity measures include - "semantic" (based on natural language inference),
                  "embedding" (based on vector embedding similarity), "embedding_large" (based on a larger embedding model),
                  "code" (based on model-based analysis designed to compare code), "discrepancy" (based on model-based analysis of possible discrepancies),
                  and "string" (based on character/word overlap). Set this to "string" for minimal runtimes.
                  This parameter has no effect when `num_consistency_samples = 0`.

                  num_candidate_responses (int, default = 1): how many alternative candidate responses are internally generated in `TLM.prompt()`.
                  `TLM.prompt()` scores the trustworthiness of each candidate response, and then returns the most trustworthy one.
                  You can auto-improve responses by increasing this parameter, but at higher runtimes/costs.
                  This parameter must be between 1 and 20. It has no effect on `TLM.score()`.
                  When this parameter is 1, `TLM.prompt()` simply returns a standard LLM response and does not attempt to auto-improve it.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  disable_trustworthiness (bool, default = False): if True, trustworthiness scoring is disabled and TLM will not compute trust scores for responses.
                  This is useful when you only want to use custom evaluation criteria or when you want to minimize computational overhead and only need the base LLM response.
                  The following parameters will be ignored when `disable_trustworthiness` is True: `num_consistency_samples`, `num_self_reflections`, `num_candidate_responses`, `reasoning_effort`, `similarity_measure`.

          quality_preset: The quality preset to use for the TLM or Trustworthy RAG API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/tlm/prompt",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "constrain_outputs": constrain_outputs,
                    "options": options,
                    "quality_preset": quality_preset,
                    "task": task,
                },
                tlm_prompt_params.TlmPromptParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TlmPromptResponse,
        )

    async def score(
        self,
        *,
        prompt: str,
        response: str,
        constrain_outputs: Optional[SequenceNotStr[str]] | NotGiven = NOT_GIVEN,
        options: Optional[tlm_score_params.Options] | NotGiven = NOT_GIVEN,
        quality_preset: Literal["best", "high", "medium", "low", "base"] | NotGiven = NOT_GIVEN,
        task: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TlmScoreResponse:
        """
        Scores the TLM API.

        TODO:

        - Track query count in DB
        - Enforce hard cap on queries for users w/o credit card on file

        Args:
          options: Typed dict of advanced configuration options for the Trustworthy Language Model.
              Many of these configurations are determined by the quality preset selected
              (learn about quality presets in the TLM [initialization method](./#class-tlm)).
              Specifying TLMOptions values directly overrides any default values set from the
              quality preset.

              For all options described below, higher settings will lead to longer runtimes
              and may consume more tokens internally. You may not be able to run long prompts
              (or prompts with long responses) in your account, unless your token/rate limits
              are increased. If you hit token limit issues, try lower/less expensive
              TLMOptions to be able to run longer prompts/responses, or contact Cleanlab to
              increase your limits.

              The default values corresponding to each quality preset are:

              - **best:** `num_consistency_samples` = 8, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **high:** `num_consistency_samples` = 4, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **medium:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"high"`.
              - **low:** `num_consistency_samples` = 0, `num_self_reflections` = 3,
                `reasoning_effort` = `"none"`.
              - **base:** `num_consistency_samples` = 0, `num_self_reflections` = 1,
                `reasoning_effort` = `"none"`.

              By default, TLM uses the: "medium" `quality_preset`, "gpt-4.1-mini" base
              `model`, and `max_tokens` is set to 512. You can set custom values for these
              arguments regardless of the quality preset specified.

              Args: model ({"gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-4.1", "gpt-4.1-mini",
              "gpt-4.1-nano", "o4-mini", "o3", "gpt-4.5-preview", "gpt-4o-mini", "gpt-4o",
              "o3-mini", "o1", "o1-mini", "gpt-4", "gpt-3.5-turbo-16k", "claude-opus-4-0",
              "claude-sonnet-4-0", "claude-3.7-sonnet", "claude-3.5-sonnet-v2",
              "claude-3.5-sonnet", "claude-3.5-haiku", "claude-3-haiku", "nova-micro",
              "nova-lite", "nova-pro"}, default = "gpt-4.1-mini"): Underlying base LLM to use
              (better models yield better results, faster models yield faster results). -
              Models still in beta: "o3", "o1", "o4-mini", "o3-mini", "o1-mini",
              "gpt-4.5-preview", "claude-opus-4-0", "claude-sonnet-4-0", "claude-3.7-sonnet",
              "claude-3.5-haiku". - Recommended models for accuracy: "gpt-5", "gpt-4.1",
              "o4-mini", "o3", "claude-opus-4-0", "claude-sonnet-4-0". - Recommended models
              for low latency/costs: "gpt-4.1-nano", "nova-micro".

                  log (list[str], default = []): optionally specify additional logs or metadata that TLM should return.
                  For instance, include "explanation" here to get explanations of why a response is scored with low trustworthiness.

                  custom_eval_criteria (list[dict[str, Any]], default = []): optionally specify custom evalution criteria beyond the built-in trustworthiness scoring.
                  The expected input format is a list of dictionaries, where each dictionary has the following keys:
                  - name: Name of the evaluation criteria.
                  - criteria: Instructions specifying the evaluation criteria.

                  max_tokens (int, default = 512): the maximum number of tokens that can be generated in the response from `TLM.prompt()` as well as during internal trustworthiness scoring.
                  If you experience token/rate-limit errors, try lowering this number.
                  For OpenAI models, this parameter must be between 64 and 4096. For Claude models, this parameter must be between 64 and 512.

                  reasoning_effort ({"none", "low", "medium", "high"}, default = "high"): how much internal LLM calls are allowed to reason (number of thinking tokens)
                  when generating alternative possible responses and reflecting on responses during trustworthiness scoring.
                  Reduce this value to reduce runtimes. Higher values may improve trust scoring.

                  num_self_reflections (int, default = 3): the number of different evaluations to perform where the LLM reflects on the response, a factor affecting trust scoring.
                  The maximum number currently supported is 3. Lower values can reduce runtimes.
                  Reflection helps quantify aleatoric uncertainty associated with challenging prompts and catches responses that are noticeably incorrect/bad upon further analysis.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  num_consistency_samples (int, default = 8): the amount of internal sampling to measure LLM response consistency, a factor affecting trust scoring.
                  Must be between 0 and 20. Lower values can reduce runtimes.
                  Measuring consistency helps quantify the epistemic uncertainty associated with
                  strange prompts or prompts that are too vague/open-ended to receive a clearly defined 'good' response.
                  TLM measures consistency via the degree of contradiction between sampled responses that the model considers plausible.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  similarity_measure ({"semantic", "string", "embedding", "embedding_large", "code", "discrepancy"}, default = "discrepancy"): how the
                  trustworthiness scoring's consistency algorithm measures similarity between alternative responses considered plausible by the model.
                  Supported similarity measures include - "semantic" (based on natural language inference),
                  "embedding" (based on vector embedding similarity), "embedding_large" (based on a larger embedding model),
                  "code" (based on model-based analysis designed to compare code), "discrepancy" (based on model-based analysis of possible discrepancies),
                  and "string" (based on character/word overlap). Set this to "string" for minimal runtimes.
                  This parameter has no effect when `num_consistency_samples = 0`.

                  num_candidate_responses (int, default = 1): how many alternative candidate responses are internally generated in `TLM.prompt()`.
                  `TLM.prompt()` scores the trustworthiness of each candidate response, and then returns the most trustworthy one.
                  You can auto-improve responses by increasing this parameter, but at higher runtimes/costs.
                  This parameter must be between 1 and 20. It has no effect on `TLM.score()`.
                  When this parameter is 1, `TLM.prompt()` simply returns a standard LLM response and does not attempt to auto-improve it.
                  This parameter has no effect when `disable_trustworthiness` is True.

                  disable_trustworthiness (bool, default = False): if True, trustworthiness scoring is disabled and TLM will not compute trust scores for responses.
                  This is useful when you only want to use custom evaluation criteria or when you want to minimize computational overhead and only need the base LLM response.
                  The following parameters will be ignored when `disable_trustworthiness` is True: `num_consistency_samples`, `num_self_reflections`, `num_candidate_responses`, `reasoning_effort`, `similarity_measure`.

          quality_preset: The quality preset to use for the TLM or Trustworthy RAG API.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/tlm/score",
            body=await async_maybe_transform(
                {
                    "prompt": prompt,
                    "response": response,
                    "constrain_outputs": constrain_outputs,
                    "options": options,
                    "quality_preset": quality_preset,
                    "task": task,
                },
                tlm_score_params.TlmScoreParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TlmScoreResponse,
        )


class TlmResourceWithRawResponse:
    def __init__(self, tlm: TlmResource) -> None:
        self._tlm = tlm

        self.prompt = to_raw_response_wrapper(
            tlm.prompt,
        )
        self.score = to_raw_response_wrapper(
            tlm.score,
        )


class AsyncTlmResourceWithRawResponse:
    def __init__(self, tlm: AsyncTlmResource) -> None:
        self._tlm = tlm

        self.prompt = async_to_raw_response_wrapper(
            tlm.prompt,
        )
        self.score = async_to_raw_response_wrapper(
            tlm.score,
        )


class TlmResourceWithStreamingResponse:
    def __init__(self, tlm: TlmResource) -> None:
        self._tlm = tlm

        self.prompt = to_streamed_response_wrapper(
            tlm.prompt,
        )
        self.score = to_streamed_response_wrapper(
            tlm.score,
        )


class AsyncTlmResourceWithStreamingResponse:
    def __init__(self, tlm: AsyncTlmResource) -> None:
        self._tlm = tlm

        self.prompt = async_to_streamed_response_wrapper(
            tlm.prompt,
        )
        self.score = async_to_streamed_response_wrapper(
            tlm.score,
        )

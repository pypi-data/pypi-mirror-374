# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import SequenceNotStr

__all__ = ["TlmPromptParams", "Options"]


class TlmPromptParams(TypedDict, total=False):
    prompt: Required[str]

    constrain_outputs: Optional[SequenceNotStr[str]]

    options: Optional[Options]
    """
    Typed dict of advanced configuration options for the Trustworthy Language Model.
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
    """

    quality_preset: Literal["best", "high", "medium", "low", "base"]
    """The quality preset to use for the TLM or Trustworthy RAG API."""

    task: Optional[str]


class Options(TypedDict, total=False):
    custom_eval_criteria: Iterable[object]

    disable_persistence: bool

    disable_trustworthiness: bool

    log: SequenceNotStr[str]

    max_tokens: int

    model: str

    num_candidate_responses: int

    num_consistency_samples: int

    num_self_reflections: int

    reasoning_effort: str

    similarity_measure: str

    use_self_reflection: bool

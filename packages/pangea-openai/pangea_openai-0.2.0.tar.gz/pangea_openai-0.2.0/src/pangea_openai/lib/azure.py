from __future__ import annotations

import os
from collections.abc import Awaitable, Callable, Mapping

import httpx
from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, AsyncStream, NotGiven, OpenAIError, Stream, Timeout
from openai.lib.azure import API_KEY_SENTINEL, AsyncAzureADTokenProvider, AzureADTokenProvider, BaseAzureClient
from typing_extensions import Any, overload, override

from pangea_openai._client import AsyncPangeaOpenAI, PangeaOpenAI


class PangeaAzureOpenAI(BaseAzureClient[httpx.Client, Stream[Any]], PangeaOpenAI):
    @overload
    def __init__(
        self,
        *,
        azure_endpoint: str,
        azure_deployment: str | None = None,
        api_version: str | None = None,
        api_key: str | Callable[[], str] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
        organization: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        azure_deployment: str | None = None,
        api_version: str | None = None,
        api_key: str | Callable[[], str] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
        organization: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        base_url: str,
        api_version: str | None = None,
        api_key: str | Callable[[], str] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
        organization: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    @override
    def __init__(
        self,
        *,
        api_version: str | None = None,
        azure_endpoint: str | None = None,
        azure_deployment: str | None = None,
        api_key: str | Callable[[], str] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AzureADTokenProvider | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        base_url: str | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None:
        """Construct a new synchronous azure openai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not
        provided:
        - `api_key` from `AZURE_OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        - `azure_ad_token` from `AZURE_OPENAI_AD_TOKEN`
        - `api_version` from `OPENAI_API_VERSION`
        - `azure_endpoint` from `AZURE_OPENAI_ENDPOINT`

        Args:
            azure_endpoint: Your Azure endpoint, including the resource, e.g. `https://example-resource.azure.openai.com/`

            azure_ad_token: Your Azure Active Directory token, https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id

            azure_ad_token_provider: A function that returns an Azure Active Directory token, will be invoked on every
                request.

            azure_deployment: A model deployment, if given with `azure_endpoint`, sets the base client URL to include
                `/deployments/{azure_deployment}`. Not supported with Assistants APIs.
        """
        if api_key is None:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        if azure_ad_token is None:
            azure_ad_token = os.environ.get("AZURE_OPENAI_AD_TOKEN")

        if api_key is None and azure_ad_token is None and azure_ad_token_provider is None:
            raise OpenAIError(
                "Missing credentials. Please pass one of `api_key`, `azure_ad_token`, `azure_ad_token_provider`, or "
                "the `AZURE_OPENAI_API_KEY` or `AZURE_OPENAI_AD_TOKEN` environment variables."
            )

        if api_version is None:
            api_version = os.environ.get("OPENAI_API_VERSION")

        if api_version is None:
            raise ValueError(
                "Must provide either the `api_version` argument or the `OPENAI_API_VERSION` environment variable"
            )

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {**default_query, "api-version": api_version}

        if base_url is None:
            if azure_endpoint is None:
                azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

            if azure_endpoint is None:
                raise ValueError(
                    "Must provide one of the `base_url` or `azure_endpoint` arguments, or the `AZURE_OPENAI_ENDPOINT` "
                    "environment variable"
                )

            if azure_deployment is not None:
                base_url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}"
            else:
                base_url = f"{azure_endpoint.rstrip('/')}/openai"
        else:
            if azure_endpoint is not None:
                raise ValueError("base_url and azure_endpoint are mutually exclusive")

        if api_key is None:
            # define a sentinel value to avoid any typing issues
            api_key = API_KEY_SENTINEL

        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            websocket_base_url=websocket_base_url,
            _strict_response_validation=_strict_response_validation,
            # Pangea
            pangea_api_key=pangea_api_key,
            pangea_input_recipe=pangea_input_recipe,
            pangea_output_recipe=pangea_output_recipe,
        )
        self._api_version = api_version
        self._azure_ad_token = azure_ad_token
        self._azure_ad_token_provider = azure_ad_token_provider
        self._azure_deployment = azure_deployment if azure_endpoint else None
        self._azure_endpoint = httpx.URL(azure_endpoint) if azure_endpoint else None


class AsyncPangeaAzureOpenAI(BaseAzureClient[httpx.AsyncClient, AsyncStream[Any]], AsyncPangeaOpenAI):
    @overload
    def __init__(
        self,
        *,
        azure_endpoint: str,
        azure_deployment: str | None = None,
        api_version: str | None = None,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AsyncAzureADTokenProvider | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        azure_deployment: str | None = None,
        api_version: str | None = None,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AsyncAzureADTokenProvider | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    @overload
    def __init__(
        self,
        *,
        base_url: str,
        api_version: str | None = None,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AsyncAzureADTokenProvider | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None: ...

    def __init__(
        self,
        *,
        azure_endpoint: str | None = None,
        azure_deployment: str | None = None,
        api_version: str | None = None,
        api_key: str | Callable[[], Awaitable[str]] | None = None,
        azure_ad_token: str | None = None,
        azure_ad_token_provider: AsyncAzureADTokenProvider | None = None,
        organization: str | None = None,
        project: str | None = None,
        webhook_secret: str | None = None,
        base_url: str | None = None,
        websocket_base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.AsyncClient | None = None,
        _strict_response_validation: bool = False,
        # Pangea
        pangea_api_key: str,
        pangea_input_recipe: str | None = None,
        pangea_output_recipe: str | None = None,
    ) -> None:
        """Construct a new asynchronous azure openai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not
        provided:
        - `api_key` from `AZURE_OPENAI_API_KEY`
        - `organization` from `OPENAI_ORG_ID`
        - `project` from `OPENAI_PROJECT_ID`
        - `azure_ad_token` from `AZURE_OPENAI_AD_TOKEN`
        - `api_version` from `OPENAI_API_VERSION`
        - `azure_endpoint` from `AZURE_OPENAI_ENDPOINT`

        Args:
            azure_endpoint: Your Azure endpoint, including the resource, e.g. `https://example-resource.azure.openai.com/`

            azure_ad_token: Your Azure Active Directory token, https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id

            azure_ad_token_provider: A function that returns an Azure Active Directory token, will be invoked on every
                request.

            azure_deployment: A model deployment, if given with `azure_endpoint`, sets the base client URL to include
                `/deployments/{azure_deployment}`. Not supported with Assistants APIs.
        """
        if api_key is None:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        if azure_ad_token is None:
            azure_ad_token = os.environ.get("AZURE_OPENAI_AD_TOKEN")

        if api_key is None and azure_ad_token is None and azure_ad_token_provider is None:
            raise OpenAIError(
                "Missing credentials. Please pass one of `api_key`, `azure_ad_token`, `azure_ad_token_provider`, or "
                "the `AZURE_OPENAI_API_KEY` or `AZURE_OPENAI_AD_TOKEN` environment variables."
            )

        if api_version is None:
            api_version = os.environ.get("OPENAI_API_VERSION")

        if api_version is None:
            raise ValueError(
                "Must provide either the `api_version` argument or the `OPENAI_API_VERSION` environment variable"
            )

        if default_query is None:
            default_query = {"api-version": api_version}
        else:
            default_query = {**default_query, "api-version": api_version}

        if base_url is None:
            if azure_endpoint is None:
                azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

            if azure_endpoint is None:
                raise ValueError(
                    "Must provide one of the `base_url` or `azure_endpoint` arguments, or the `AZURE_OPENAI_ENDPOINT` "
                    "environment variable"
                )

            if azure_deployment is not None:
                base_url = f"{azure_endpoint.rstrip('/')}/openai/deployments/{azure_deployment}"
            else:
                base_url = f"{azure_endpoint.rstrip('/')}/openai"
        else:
            if azure_endpoint is not None:
                raise ValueError("base_url and azure_endpoint are mutually exclusive")

        if api_key is None:
            # define a sentinel value to avoid any typing issues
            api_key = API_KEY_SENTINEL

        super().__init__(  # type: ignore[call-overload,misc]
            api_key=api_key,
            organization=organization,
            project=project,
            webhook_secret=webhook_secret,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            websocket_base_url=websocket_base_url,
            _strict_response_validation=_strict_response_validation,
            # Pangea
            pangea_api_key=pangea_api_key,
            pangea_input_recipe=pangea_input_recipe,
            pangea_output_recipe=pangea_output_recipe,
        )
        self._api_version = api_version
        self._azure_ad_token = azure_ad_token
        self._azure_ad_token_provider = azure_ad_token_provider
        self._azure_deployment = azure_deployment if azure_endpoint else None
        self._azure_endpoint = httpx.URL(azure_endpoint) if azure_endpoint else None


from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from .evaluator import EvaluatorInScope
from .providers.base import ProviderType
from .providers.gradio import GradioProvider
from .providers.hf import HFProvider
from .providers.http import HttpProvider
from .providers.litellm import LitellmProvider
from .providers.ollama import OllamaProvider
from .providers.openai import OpenaiProvider
from .tactic import PromptMutationTactic
from .template.prompts.base import PromptsRepoType
from .template.prompts.langhub import LangHubPromptTemplate
from .template.prompts.app import AppPromptTemplate


class AgentInfo(BaseModel):
    """Represents an AI agent with integrations, capabilities, and restrictions."""

    name: Optional[str] = Field(default_factory=lambda: "")
    description: str
    external_integrations: Optional[List[str]] = Field(default_factory=list)
    internal_integrations: Optional[List[str]] = Field(default_factory=list)
    trusted_users: Optional[List[str]] = Field(default_factory=list)
    untrusted_users: Optional[List[str]] = Field(default_factory=list)
    llms: Optional[List[str]] = Field(default_factory=list)
    capabilities: Optional[List[str]] = Field(default_factory=list)
    restrictions: Optional[List[str]] = Field(default_factory=list)
    security_note: Optional[str] = Field(default_factory=str)
    include_attacker_goals: Optional[List[str]] = Field(default_factory=list)


class RiskTaxonomy(Enum):
    """Enum representing different risk taxonomies."""

    DETOXIO = "DETOXIO"
    OWASP_2025 = "OWASP_2025"

    def __str__(self):
        return self.value

    @classmethod
    def values(cls) -> List[str]:
        return [member.value for member in cls]


class PluginTaxonomyMapping(BaseModel):
    """Provides mapping between plugins and different taxonomies."""

    taxonomy: RiskTaxonomy
    category: str
    id: str
    title: str


class Plugin(BaseModel):
    """Represents a Plugin entry."""

    id: str
    title: str
    name: str
    category: str
    subcategory: str
    summary: Optional[str] = None
    taxonomy_mappings: Optional[List[PluginTaxonomyMapping]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)


class PluginInScopeConfig(BaseModel):
    """Configuration for each plugin with an ID and number of tests."""

    id: str
    num_tests: int = 5


class PluginsInScope(BaseModel):
    """
    Represents a collection of plugins:
    - Either plugin IDs (str)
    - Or PluginInScopeConfig objects
    """

    plugins: List[Union[str, PluginInScopeConfig]]

    def get_plugin_ids(self) -> List[str]:
        ids = []
        for p in self.plugins:
            ids.append(p if isinstance(p, str) else p.id)
        return ids


class RedTeamSettings(BaseModel):
    """Settings for red teaming."""

    max_prompts: int = 15
    max_plugins: int = 5
    max_prompts_per_plugin: int = 5
    max_goals_per_plugin: int = 1
    max_prompts_per_tactic: int = 5
    plugins: PluginsInScope
    tactics: Optional[List[PromptMutationTactic]] = Field(
        default_factory=list,
        description="Strategies to perform red teaming",
    )
    global_evaluator: Optional[EvaluatorInScope] = Field(
        default=None,
        description="Optional global evaluator to override all evaluation methods",
    )


class ProviderVars(BaseModel):
    """Holds provider variables, possibly with `{{env.ENV_NAME}}` placeholders."""

    vars: Dict[str, Any] = Field(default_factory=dict)


class ProvidersWithEnvironments(BaseModel):
    """Holds providers, prompts, and environment variables for red teaming."""

    providers: Optional[
        List[
            HttpProvider
            | HFProvider
            | GradioProvider
            | OllamaProvider
            | OpenaiProvider
            | LitellmProvider
        ]
    ] = Field(default_factory=list, description="List of providers to test")

    prompts: Optional[List[LangHubPromptTemplate | AppPromptTemplate]] = Field(
        default_factory=list, description="List of prompt templates to test"
    )

    environments: Optional[List[ProviderVars]] = Field(
        default_factory=list, description="Environment variables for providers"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_providers(cls, values):
        """Instantiate correct provider type based on 'provider' field."""
        providers_data = values.get("providers", [])
        parsed = []

        for provider_data in providers_data:
            if isinstance(provider_data, dict):
                provider_id = provider_data.get("provider")
                if provider_id == ProviderType.HTTP.value:
                    parsed.append(HttpProvider(**provider_data))
                elif provider_id == ProviderType.GRADIO.value:
                    parsed.append(GradioProvider(**provider_data))
                elif provider_id == ProviderType.HF.value:
                    parsed.append(HFProvider(**provider_data))
                elif provider_id == ProviderType.OLLAMA.value:
                    parsed.append(OllamaProvider(**provider_data))
                elif provider_id == ProviderType.OPENAI.value:
                    parsed.append(OpenaiProvider(**provider_data))
                elif provider_id == ProviderType.LITE_LLM.value:
                    parsed.append(LitellmProvider(**provider_data))
                else:
                    raise ValueError(f"Unknown provider type: {provider_id}")
            else:
                parsed.append(provider_data)

        values["providers"] = parsed
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_prompts(cls, values):
        """Instantiate correct prompt type based on 'provider' field."""
        prompts_data = values.get("prompts", [])
        parsed = []

        for prompt_data in prompts_data:
            if isinstance(prompt_data, dict):
                prompt_id = prompt_data.get("provider")
                if prompt_id == PromptsRepoType.LANGHUB.value:
                    parsed.append(LangHubPromptTemplate(**prompt_data))
                elif prompt_id == PromptsRepoType.APP.value:
                    parsed.append(AppPromptTemplate(**prompt_data))
                else:
                    raise ValueError(f"Unknown prompt repo type: {prompt_id}")
            else:
                parsed.append(prompt_data)

        values["prompts"] = parsed
        return values


class RedTeamScope(ProvidersWithEnvironments):
    """Represents a red teaming scope, including agent info and settings."""

    agent: AgentInfo
    redteam: RedTeamSettings

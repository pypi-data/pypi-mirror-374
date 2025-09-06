# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ToolSetVendor(BaseModel):
    """Vendor Toolsets info."""

    name: str = Field(
        ...,
        title="Vendor Name",
        description="The name of the vendor providing the tool or agent.",
    )

    description: str = Field(
        ...,
        title="Vendor Description",
        description="A brief description of the vendor.",
    )

    url: str = Field(..., title="Vendor URL", description="The URL of vendor.")

    svg: str = Field(
        ..., title="Vendor SVG Icon", description="The SVG icon of the vendor."
    )


class OptionalToolSet(BaseModel):
    """Describes the toolsets of a Sec-Gemini model."""

    name: str = Field(..., title="toolset Name", description="The name of the toolset.")
    version: int = Field(
        ..., title="toolset Version", description="The version of the toolset."
    )
    description: Optional[str] = Field(
        None,
        title="toolset Description",
        description="A brief description of the toolset.",
    )
    vendor: ToolSetVendor = Field(
        ..., title="toolset Vendor", description="The vendor of the toolset."
    )

    # This is deprecated, and will be removed in the future. Use is_enabled_by_default
    is_enabled: bool = Field(
        True, title="Is Enabled", description="Whether the toolset is enabled or not."
    )
    is_enabled_by_default: bool = Field(
        ...,
        title="Is Bundle Enabled by default",
        description="Whether the bundle is enabled by default or not.",
    )
    is_enabled_by_default_in_incognito: bool = Field(
        ...,
        title="Is Bundle Enabled by default in incognito mode?",
        description="Whether this tool is enabled in incognito mode by default.",
    )

    is_experimental: bool = Field(
        False,
        title="Is Experimental",
        description="Whether the toolset is experimental or not.",
    )


class ModelInfo(BaseModel):
    """Describes a Sec-Gemini model."""

    model_name: str = Field(
        ..., title="Model name", description="The string used to identify the model."
    )
    version: str = Field(
        ..., title="Model Version", description="The version of the model."
    )
    use_experimental: bool = Field(
        False,
        title="Use Experimental",
        description="Whether to use experimental sub agents and tools.",
    )
    model_string: str = Field(
        ..., title="Model String", description="The string used to identify the model."
    )
    description: Optional[str] = Field(
        "", title="Model Description", description="A brief description of the model."
    )
    toolsets: list[OptionalToolSet] = Field(
        default_factory=list,
        title="Tools",
        description="Toggable tools used by the model.",
    )

    @staticmethod
    def get_model_info_from_model_string(model_string: str) -> ModelInfo:
        try:
            if model_string.endswith("-experimental"):
                use_experimental = True
                parts = model_string.rsplit("-", 2)
                model_name, version = parts[0], parts[1]
                assert parts[2] == "experimental"
            else:
                use_experimental = False
                parts = model_string.rsplit("-", 1)
                model_name, version = parts[0], parts[1]
        except Exception:
            raise ValueError(f"Invalid model string as input: {model_string}")
        return ModelInfo(
            model_name=model_name,
            version=version,
            use_experimental=use_experimental,
            model_string=model_string,
            description="",
            toolsets=[],
        )

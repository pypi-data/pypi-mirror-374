from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Type, Union
from uuid import UUID
from pydantic import BaseModel
import json
import textwrap
import re


from spof import json_util


class RenderFormat(str, Enum):
    XML = "xml"
    MARKDOWN = "markdown"
    JSON = "json"


def _camel_to_snake(name: str) -> str:
    """Convert CamelCase to snake_case"""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _get_model_fields(
    model: BaseModel, exclude_fields: Optional[List[str]] = None
) -> Iterable[Tuple[str, Any]]:
    """Get all model fields and values of the fields (Pydantic v1/v2 compatible) with optional exclusions"""
    field_names: Sequence[str]

    if hasattr(model, "model_fields"):
        # Pydantic v2
        field_names = list(getattr(model, "model_fields").keys())
    else:
        # Pydantic v1
        field_names = list(getattr(model, "__fields__").keys())

    # Default exclusions
    default_excludes = ["format_preference"]  # Format preference is spof internal field
    exclude_fields = exclude_fields or []
    all_excludes = default_excludes + exclude_fields

    for name in field_names:
        if name in all_excludes:
            continue
        yield name, getattr(model, name, None)  # Yield field name and value


def _coerce_str(x: Any) -> str:
    """Convert any value to string"""
    return x if isinstance(x, str) else str(x)


class InstructionBlock(BaseModel, ABC):
    """Base class for all instruction blocks"""

    format_preference: RenderFormat = RenderFormat.XML
    __block_name__: Optional[str] = None

    @classmethod
    def block_name(cls) -> str:
        """Get the block name"""
        if getattr(cls, "__block_name__", None):
            return getattr(cls, "__block_name__")

        Config = getattr(cls, "Config", None)
        if Config is not None and hasattr(Config, "name"):
            name = getattr(Config, "name")
            if isinstance(name, str) and name:
                return name

        # Last resort: convert class name from CamelCase to snake_case
        return _camel_to_snake(cls.__name__)

    def get_block_name(self) -> str:
        """Get the block name for this instance, checking instance attributes first"""
        # Check instance attribute first (set in __init__)
        if hasattr(self, "__block_name__") and getattr(self, "__block_name__", None):
            return getattr(self, "__block_name__")

        # Fall back to class method
        return self.block_name()

    def _get_fields_for_rendering(self):
        """Get fields to render - can be overridden by subclasses"""
        return _get_model_fields(self)

    def render(self, format: RenderFormat = None, indent_level: int = 0) -> str:
        """Render the block to the required format"""
        fmt = format or self.format_preference
        name = self.get_block_name()  # Use instance method instead of class method

        if fmt == RenderFormat.XML:
            inner_items = []
            for f, v in self._get_fields_for_rendering():
                rendered_field = self._render_field_xml(f, v, indent_level + 1)
                if rendered_field:
                    inner_items.append(rendered_field)

            base_indent = "  " * indent_level
            inner_indent = "  " * (indent_level + 1)

            if inner_items:
                inner = (
                    f"\n{inner_indent}".join([""] + inner_items) + f"\n{base_indent}"
                )
                return f"{base_indent}<{name}>{inner}</{name}>"
            else:
                return f"{base_indent}<{name}></{name}>"

        elif fmt == RenderFormat.MARKDOWN:
            title = name.replace("_", " ").title()
            body = "\n".join(
                self._render_field_md(f, v) for f, v in self._get_fields_for_rendering()
            )
            return f"## {title}\n\n{body}" if body else f"## {title}"

        elif fmt == RenderFormat.JSON:
            return json.dumps(
                json_util.sanitize_json(self.to_struct()), indent=2, ensure_ascii=False
            )

        raise ValueError(f"Unsupported render format: {fmt}")

    def _render_field_xml(self, field: str, value: Any, indent_level: int = 0) -> str:
        """Render a single field as XML with proper indentation"""
        base_indent = "  " * indent_level  # Base indentation at this level
        inner_indent = "  " * (indent_level + 1)

        if isinstance(value, InstructionBlock):
            # Special handling for Text blocks - render content directly with field name
            if hasattr(value, "content") and len(list(_get_model_fields(value))) == 1:
                # This is a Text block with just content - render directly
                content = getattr(value, "content", "")
                return f"{base_indent}<{field}>{_coerce_str(content)}</{field}>"
            else:
                # Regular InstructionBlock - render with its own structure
                return value.render(RenderFormat.XML, indent_level)
        if isinstance(value, BaseModel):
            # Use the field name as the block name instead of "model_block"
            return ModelBlock(value, block_name=field).render(
                RenderFormat.XML,
                indent_level,
            )
        if isinstance(value, list):
            # Handle List[InstructionBlock] or List[BaseModel] with proper rendering
            items = []
            has_instruction_blocks = False

            for v in value:
                if v is not None:
                    if isinstance(v, InstructionBlock):
                        has_instruction_blocks = True
                        # For Text blocks in lists, use their block name or a generic item name
                        if (
                            hasattr(v, "content")
                            and len(list(_get_model_fields(v))) == 1
                        ):
                            block_name = (
                                getattr(v, "__block_name__", None) or f"{field}_item"
                            )
                            content = getattr(v, "content", "")
                            items.append(
                                f"{inner_indent}<{block_name}>{_coerce_str(content)}</{block_name}>"
                            )
                        else:
                            items.append(v.render(RenderFormat.XML, indent_level + 1))
                    elif isinstance(v, BaseModel):
                        has_instruction_blocks = True
                        # Use field name + "_item" instead of "model_block"
                        item_name = (
                            getattr(v, "__block_name__", None) or f"{field}_item"
                        )
                        items.append(
                            ModelBlock(v, block_name=item_name).render(
                                RenderFormat.XML,
                                indent_level + 1,
                            )
                        )
                    else:
                        # Plain string - render as bullet point
                        items.append(f"{inner_indent}- {_coerce_str(v)}")

            if items:
                # For List[str] (no instruction blocks), render as bullet points
                if not has_instruction_blocks:
                    content = (
                        f"\n{inner_indent}".join([""] + items) + f"\n{base_indent}"
                    )
                    return f"{base_indent}<{field}>{content}</{field}>"
                else:
                    # For List[InstructionBlock], render as nested XML
                    content = (
                        f"\n{inner_indent}".join([""] + items) + f"\n{base_indent}"
                    )
                    return f"{base_indent}<{field}>{content}</{field}>"
            else:
                return f"{base_indent}<{field}></{field}>"

        if isinstance(value, dict):
            # Handle dictionaries with potential InstructionBlock values
            items = []
            for k, v in value.items():
                if isinstance(v, InstructionBlock):
                    if hasattr(v, "content") and len(list(_get_model_fields(v))) == 1:
                        content = getattr(v, "content", "")
                        items.append(f"{inner_indent}<{k}>{_coerce_str(content)}</{k}>")
                    else:
                        rendered = v.render(RenderFormat.XML, indent_level + 1)
                        # Replace the block name with the dictionary key
                        items.append(rendered.replace(v.block_name(), k, 1))
                else:
                    items.append(f"{inner_indent}<{k}>{_coerce_str(v)}</{k}>")

            if items:
                content = f"\n{inner_indent}".join([""] + items) + f"\n{base_indent}"
                return f"{base_indent}<{field}>{content}</{field}>"
            else:
                return f"{base_indent}<{field}></{field}>"

        return f"{base_indent}<{field}>{_coerce_str(value)}</{field}>"

    def _render_field_md(self, field: str, value: Any) -> str:
        """Render a single field as Markdown"""
        if isinstance(value, InstructionBlock):
            # Special handling for Text blocks - render content directly
            if hasattr(value, "content") and len(list(_get_model_fields(value))) == 1:
                content = getattr(value, "content", "")
                return f"**{field.replace('_', ' ').title()}:** {_coerce_str(content)}"
            else:
                return value.render(RenderFormat.MARKDOWN)
        if isinstance(value, BaseModel):
            return ModelBlock(value, block_name=field).render(RenderFormat.MARKDOWN)
        if isinstance(value, list):
            # Handle List[InstructionBlock] or List[BaseModel] with proper rendering
            items = []
            has_instruction_blocks = False
            for v in value:
                if v is not None:
                    if isinstance(v, InstructionBlock):
                        has_instruction_blocks = True
                        if (
                            hasattr(v, "content")
                            and len(list(_get_model_fields(v))) == 1
                        ):
                            content = getattr(v, "content", "")
                            items.append(f"- {_coerce_str(content)}")
                        else:
                            items.append(v.render(RenderFormat.MARKDOWN))
                    elif isinstance(v, BaseModel):
                        item_name = (
                            getattr(v, "__block_name__", None) or f"{field}_item"
                        )
                        items.append(
                            ModelBlock(v, block_name=item_name).render(
                                RenderFormat.MARKDOWN,
                            )
                        )
                    else:
                        items.append(f"- {_coerce_str(v)}")

            if items:
                # For List[str] (no instruction blocks), wrap with variable tags
                if not has_instruction_blocks:
                    content = "\n".join(items)
                    return f"<{field}>\n{content}\n</{field}>"
                else:
                    return "\n".join(items)
            return ""
        return f"**{field.replace('_', ' ').title()}:** {_coerce_str(value)}"

    def to_struct(self) -> Dict[str, Any]:
        """Convert to dictionary structure - your excellent addition"""
        name = self.block_name()
        body: Dict[str, Any] = {}
        for field_name, value in self._get_fields_for_rendering():
            body[field_name] = self._value_to_struct_with_context(value, field_name)
        return {name: body if body else None}

    def _value_to_struct_with_context(
        self, value: Any, field_name: Optional[str] = None
    ) -> Any:
        """Convert value to structured format with field context"""
        if isinstance(value, InstructionBlock):
            # Special handling for Text blocks - return content directly
            if hasattr(value, "content") and len(list(_get_model_fields(value))) == 1:
                return getattr(value, "content", "")
            else:
                return value.to_struct()
        if isinstance(value, BaseModel):
            # Use field name as block name if available
            return ModelBlock(value, block_name=field_name).to_struct()
        if isinstance(value, list):
            item_name = getattr(value, "__block_name__", None) or (
                f"{field_name}_item" if field_name else None
            )
            return [self._value_to_struct_with_context(v, item_name) for v in value]
        if isinstance(value, dict):
            return {
                k: self._value_to_struct_with_context(v, k) for k, v in value.items()
            }
        return value

    def _value_to_struct(self, value: Any) -> Any:
        """Convert value to structured format (legacy method)"""
        return self._value_to_struct_with_context(value, None)

    # MY UX IMPROVEMENTS - Make it as easy as Pydantic!
    def __str__(self) -> str:
        """Natural string conversion"""
        return self.render()

    def __repr__(self) -> str:
        """Better representation"""
        return f"<{self.__class__.__name__}: {self.block_name()}>"

    def to_xml(self) -> str:
        """Convenient XML output with proper indentation"""
        return self.render(RenderFormat.XML, 0)

    def to_markdown(self) -> str:
        """Convenient Markdown output"""
        return self.render(RenderFormat.MARKDOWN)

    def to_json(self) -> str:
        """Convenient JSON output"""
        return self.render(RenderFormat.JSON)


class ModelBlock(InstructionBlock):
    """Adapter to wrap any Pydantic model - your brilliant pattern!"""

    __block_name__: Optional[str] = None
    _model: BaseModel
    _exclude_fields: Optional[List[str]] = None

    def __init__(
        self,
        model: BaseModel,
        block_name: Optional[str] = None,
        exclude_fields: Optional[List[str]] = None,
    ):
        super().__init__()
        object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_exclude_fields", exclude_fields or [])
        if block_name:
            object.__setattr__(self, "__block_name__", block_name)

    @classmethod
    def block_name(cls) -> str:
        if getattr(cls, "__block_name__", None):
            return getattr(cls, "__block_name__")
        return _camel_to_snake(cls.__name__)

    def _get_fields_for_rendering(self):
        """Override to use wrapped model fields instead of self"""
        return _get_model_fields(self._model, exclude_fields=self._exclude_fields)


# EASY-TO-USE EXTENSIONS
class Text(InstructionBlock):
    """Simple text block"""

    content: str

    def __init__(self, content: str, block_name: Optional[str] = None, **kwargs):
        super().__init__(content=content, **kwargs)
        if block_name:
            object.__setattr__(self, "__block_name__", block_name)


class Items(InstructionBlock):
    """Simple list block"""

    items: List[str]

    def __init__(self, items: List[str], block_name: Optional[str] = None, **kwargs):
        super().__init__(items=items, **kwargs)
        if block_name:
            object.__setattr__(self, "__block_name__", block_name)

    def get_block_name(self) -> str:
        """Get the block name for this instance, checking instance attributes first"""
        # Check instance attribute first (set in __init__)
        if hasattr(self, "__block_name__") and getattr(self, "__block_name__", None):
            return getattr(self, "__block_name__")
        # Fall back to class method
        return self.block_name()

    def render(self, format: RenderFormat = None, indent_level: int = 0) -> str:
        """Render the block using instance-specific block name"""
        fmt = format or self.format_preference
        name = self.get_block_name()  # Use instance method instead of class method

        if fmt == RenderFormat.XML:
            # For Items, render the list directly without nested field structure
            base_indent = "  " * indent_level
            inner_indent = "  " * (indent_level + 1)

            if self.items:
                items_content = []
                for item in self.items:
                    items_content.append(f"{inner_indent}- {_coerce_str(item)}")
                content = "\n" + "\n".join(items_content) + f"\n{base_indent}"
                return f"{base_indent}<{name}>{content}</{name}>"
            else:
                return f"{base_indent}<{name}></{name}>"

        elif fmt == RenderFormat.JSON:
            return self.to_struct()
        elif fmt == RenderFormat.MARKDOWN:
            return self._render_markdown(indent_level)
        else:
            return str(self)

    def _render_markdown(self, indent_level: int = 0) -> str:
        """Render Items as markdown list"""
        base_indent = "  " * indent_level
        items_text = []
        for item in self.items:
            items_text.append(f"{base_indent}- {item}")
        return "\n".join(items_text)


def wrap_model(
    model: BaseModel,
    block_name: Optional[str] = None,
    exclude_fields: Optional[List[str]] = None,
) -> ModelBlock:
    """Convenience function to wrap any Pydantic model with optional field exclusions"""
    return ModelBlock(model, block_name, exclude_fields)

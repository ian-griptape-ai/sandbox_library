from __future__ import annotations

from typing import Any

from griptape.artifacts import ImageArtifact, ImageUrlArtifact

from griptape_nodes.exe_types.core_types import Parameter, ParameterList, ParameterMode, ParameterTypeBuiltin
from griptape_nodes.exe_types.node_types import DataNode


class ParameterListInputDebug(DataNode):
    """Debug node for testing ParameterList behavior with various list inputs."""

    def __init__(self, name: str, metadata: dict[Any, Any] | None = None) -> None:
        super().__init__(name, metadata)

        # Untyped ParameterList (no input_types) - should accept generic "list" inputs.
        self.add_parameter(
            ParameterList(
                name="untyped_items",
                tooltip="Untyped ParameterList (no input_types). Connect a generic list here.",
                default_value=[],
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"display_name": "Untyped Items"},
            )
        )

        # Typed ParameterList - explicitly supports image artifacts and list variants.
        self.add_parameter(
            ParameterList(
                name="typed_items",
                tooltip="Typed ParameterList (image artifacts + list variants).",
                input_types=[
                    "ImageArtifact",
                    "ImageUrlArtifact",
                    "list",
                    "list[ImageArtifact]",
                    "list[ImageUrlArtifact]",
                ],
                default_value=[],
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"display_name": "Typed Items"},
            )
        )

        self.add_parameter(
            Parameter(
                name="summary",
                tooltip="Summary of list contents (types, counts, and key fields).",
                type=ParameterTypeBuiltin.STR.value,
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"display_name": "Summary", "multiline": True},
            )
        )

    def process(self) -> None:
        untyped_items = self.get_parameter_list_value("untyped_items")
        typed_items = self.get_parameter_list_value("typed_items")

        lines: list[str] = []
        lines.append(f"untyped_items: {len(untyped_items)} item(s)")
        lines.extend(self._format_items(untyped_items))
        lines.append("")
        lines.append(f"typed_items: {len(typed_items)} item(s)")
        lines.extend(self._format_items(typed_items))

        self.parameter_output_values["summary"] = "\n".join(lines)

    def _format_items(self, items: list[Any]) -> list[str]:
        lines: list[str] = []
        for idx, item in enumerate(items):
            if isinstance(item, ImageUrlArtifact):
                url = item.value
                truncated = url if len(url) <= 80 else f"{url[:77]}..."
                lines.append(f"- [{idx}] ImageUrlArtifact(value={truncated!r})")
                continue

            if isinstance(item, ImageArtifact):
                byte_len = self._safe_len_bytes(item)
                lines.append(f"- [{idx}] ImageArtifact(bytes={byte_len})")
                continue

            lines.append(f"- [{idx}] {type(item).__name__}: {item!r}")

        return lines

    def _safe_len_bytes(self, artifact: ImageArtifact) -> int:
        try:
            return len(artifact.to_bytes())
        except Exception:
            return -1

from __future__ import annotations

from typing import Any

from griptape.artifacts import ImageArtifact, ImageUrlArtifact

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode, ParameterTypeBuiltin
from griptape_nodes.exe_types.node_types import DataNode


class ParameterListInputDebug(DataNode):
    """Debug node that summarizes an untyped list input."""

    def __init__(self, name: str, metadata: dict[Any, Any] | None = None) -> None:
        super().__init__(name, metadata)

        # Untyped list input (INPUT-only) - this should be provided via connection.
        self.add_parameter(
            Parameter(
                name="items",
                tooltip="Untyped list input. Connect a list to this parameter.",
                type="list",
                input_types=["list"],
                default_value=None,
                allowed_modes={ParameterMode.INPUT},
                ui_options={"display_name": "Items", "hide_property": True},
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
        items = self.get_parameter_value("items")
        if items is None:
            self.parameter_output_values["summary"] = "items: 0 item(s)"
            return

        if not isinstance(items, list):
            self.parameter_output_values["summary"] = f"items: expected list, got {type(items).__name__}"
            return

        lines: list[str] = []
        lines.append(f"items: {len(items)} item(s)")
        lines.extend(self._format_items(items))

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

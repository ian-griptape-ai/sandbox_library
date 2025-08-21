from typing import Any, Tuple, Dict
import requests
from requests.exceptions import RequestException
from io import BytesIO

from griptape.artifacts import ImageUrlArtifact
from PIL import Image

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import BaseNode, DataNode
from griptape_nodes.traits.options import Options
from griptape_nodes_library.utils.image_utils import (
    dict_to_image_url_artifact,
    load_pil_from_url,
    save_pil_image_to_static_file,
)


# Common aspect ratio presets (pure ratios without fixed pixels)
ASPECT_RATIO_PRESETS = {
    "custom": None,  # Custom option allows manual dimensions
    "1:1 square": (1, 1),
    "3:4 portrait": (3, 4),
    "5:8 portrait": (5, 8),
    "9:16 portrait": (9, 16),
    "9:21 portrait": (9, 21),
    "4:3 landscape": (4, 3),
    "3:2 landscape": (3, 2),
    "16:9 landscape": (16, 9),
    "21:9 landscape": (21, 9),
    "2:1 landscape": (2, 1),
    "3:1 landscape": (3, 1),
    "4:1 landscape": (4, 1),
    "5:1 landscape": (5, 1),
    "1:2 portrait": (1, 2),
    "1:3 portrait": (1, 3),
    "1:4 portrait": (1, 4),
    "1:5 portrait": (1, 5),
    "2:3 portrait": (2, 3),
    "3:4 portrait": (3, 4),
    "4:5 portrait": (4, 5),
    "5:6 portrait": (5, 6),
    "6:7 portrait": (6, 7),
    "7:8 portrait": (7, 8),
    "8:9 portrait": (8, 9),
    "9:10 portrait": (9, 10),
    "10:11 portrait": (10, 11),
    "11:12 portrait": (11, 12),
    "12:13 portrait": (12, 13),
    "13:14 portrait": (13, 14),
    "14:15 portrait": (14, 15),
    "15:16 portrait": (15, 16),
    "16:10 landscape": (16, 10),
    "10:16 portrait": (10, 16),
    "16:12 landscape": (16, 12),
    "12:16 portrait": (12, 16),
    "18:9 landscape": (18, 9),
    "9:18 portrait": (9, 18),
    "19:9 landscape": (19, 9),
    "9:19 portrait": (9, 19),
    "20:9 landscape": (20, 9),
    "9:20 portrait": (9, 20),
    "22:9 landscape": (22, 9),
    "9:22 portrait": (9, 22),
    "24:9 landscape": (24, 9),
    "9:24 portrait": (9, 24),
    "32:9 landscape": (32, 9),
    "9:32 portrait": (9, 32),
}


class ExtendAspectRatio(DataNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.category = "Image"
        self.description = "Extend image aspect ratio and generate a mask showing original vs extended areas"

        # Input image parameter
        self.add_parameter(
            Parameter(
                name="input_image",
                default_value=None,
                input_types=["ImageArtifact", "ImageUrlArtifact", "str"],
                output_type="ImageUrlArtifact",
                type="ImageUrlArtifact",
                tooltip="The input image to extend (can be an image, URL, or file path)",
                ui_options={"hide_property": True},
                allowed_modes={ParameterMode.INPUT, ParameterMode.OUTPUT},
            )
        )

        # Aspect ratio preset parameter
        self.add_parameter(
            Parameter(
                name="aspect_ratio_preset",
                input_types=["str"],
                type="str",
                output_type="str",
                tooltip="Select a preset aspect ratio or 'custom' to set manual dimensions",
                default_value="1:1 square 1024x1024",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                traits={Options(choices=list(ASPECT_RATIO_PRESETS.keys()))},
            )
        )

        # Upscale factor parameter
        self.add_parameter(
            Parameter(
                name="upscale_factor",
                input_types=["float"],
                type="float",
                output_type="float",
                tooltip="Factor to upscale the calculated dimensions",
                default_value=1.0,
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
            )
        )



        # Output extended image
        self.add_parameter(
            Parameter(
                name="extended_image",
                input_types=["ImageArtifact", "ImageUrlArtifact"],
                type="ImageUrlArtifact",
                tooltip="The extended image with new aspect ratio",
                ui_options={"expander": True},
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

        # Output mask
        self.add_parameter(
            Parameter(
                name="extension_mask",
                input_types=["ImageArtifact", "ImageUrlArtifact"],
                type="ImageUrlArtifact",
                tooltip="Mask where black = original image, white = extended areas",
                ui_options={"expander": True},
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def process(self) -> None:
        input_image = self.get_parameter_value("input_image")
        if input_image is None:
            return

        # Normalize input to ImageUrlArtifact
        if isinstance(input_image, dict):
            input_image = dict_to_image_url_artifact(input_image)
        elif isinstance(input_image, str):
            # Handle direct URL or file path string input
            try:
                # Check if it's a URL (starts with http/https)
                if input_image.startswith(('http://', 'https://')):
                    try:
                        response = requests.get(input_image, stream=True, timeout=10)
                        response.raise_for_status()
                        img = Image.open(BytesIO(response.content))
                        # Convert PIL image to ImageUrlArtifact
                        input_image = save_pil_image_to_static_file(img)
                    except RequestException as re:
                        raise ValueError(f"Error downloading image from URL: {str(re)}")
                    except Exception as e:
                        raise ValueError(f"Error processing downloaded image: {str(e)}")
                else:
                    # Treat as a local file path
                    try:
                        img = Image.open(input_image)
                        input_image = save_pil_image_to_static_file(img)
                    except Exception as e:
                        raise ValueError(f"Error opening local image file: {str(e)}")
            except Exception as e:
                raise ValueError(f"Error processing image input: {str(e)}")

        # Get parameters
        aspect_ratio_preset = self.get_parameter_value("aspect_ratio_preset")
        # Use fixed values for hidden parameters
        extension_direction = "center"
        background_color = "black"

        # Get upscale factor
        upscale_factor = self.get_parameter_value("upscale_factor")
        
        # Calculate target dimensions
        if aspect_ratio_preset != "custom" and aspect_ratio_preset in ASPECT_RATIO_PRESETS:
            # Get the ratio from preset
            ratio_width, ratio_height = ASPECT_RATIO_PRESETS[aspect_ratio_preset]
            
            # Load original image to get current dimensions
            original_image = load_pil_from_url(input_image.value)
            original_width, original_height = original_image.size
            
            # Calculate target dimensions based on original image size and ratio
            # We'll maintain the larger dimension and calculate the other based on the ratio
            if original_width / original_height > ratio_width / ratio_height:
                # Original image is wider than target ratio, extend height
                target_width = original_width
                target_height = int(original_width * ratio_height / ratio_width)
            else:
                # Original image is taller than target ratio, extend width
                target_height = original_height
                target_width = int(original_height * ratio_width / ratio_height)
        else:
            # For custom mode, use original image dimensions as base
            original_image = load_pil_from_url(input_image.value)
            target_width, target_height = original_image.size
        
        # Apply upscale factor
        if upscale_factor != 1.0:
            target_width = int(target_width * upscale_factor)
            target_height = int(target_height * upscale_factor)

        # Process the image
        self._extend_image(input_image, target_width, target_height, extension_direction, background_color)

    def after_incoming_connection(
        self,
        source_node: BaseNode,
        source_parameter: Parameter,
        target_parameter: Parameter,
    ) -> None:
        """Handle input connections and update outputs accordingly."""
        # Don't auto-process - let user run manually
        return super().after_incoming_connection(source_node, source_parameter, target_parameter)

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        # Don't auto-process - let user run manually
        return super().after_value_set(parameter, value)



    def _extend_image(
        self, 
        image_artifact: ImageUrlArtifact, 
        target_width: int, 
        target_height: int, 
        extension_direction: str, 
        background_color: str
    ) -> None:
        """Extend the image and create the mask."""
        # Load original image
        original_image = load_pil_from_url(image_artifact.value)
        original_width, original_height = original_image.size

        # Ensure we're actually extending (target should be larger than original)
        # If target is smaller, we'll use the larger of the two dimensions
        final_width = max(target_width, original_width)
        final_height = max(target_height, original_height)

        # Create new canvas with the final dimensions
        if background_color == "transparent":
            new_image = Image.new("RGBA", (final_width, final_height), (0, 0, 0, 0))
            mask_image = Image.new("RGBA", (final_width, final_height), (0, 0, 0, 0))
        else:
            bg_color = (0, 0, 0) if background_color == "black" else (255, 255, 255)
            new_image = Image.new("RGB", (final_width, final_height), bg_color)
            mask_image = Image.new("RGB", (final_width, final_height), (255, 255, 255))  # White background for mask

        # Calculate position for original image
        x, y = self._calculate_position(original_width, original_height, final_width, final_height, extension_direction)

        # Paste original image
        new_image.paste(original_image, (x, y))

        # Create mask (black for original image, white for extended areas)
        if background_color == "transparent":
            # For transparent background, create alpha-based mask
            mask_image.paste((0, 0, 0, 255), (x, y, x + original_width, y + original_height))
        else:
            # For solid background, create RGB mask
            mask_image.paste((0, 0, 0), (x, y, x + original_width, y + original_height))

        # Save outputs
        extended_artifact = save_pil_image_to_static_file(new_image)
        mask_artifact = save_pil_image_to_static_file(mask_image)

        # Set outputs
        self.set_parameter_value("extended_image", extended_artifact)
        self.set_parameter_value("extension_mask", mask_artifact)
        
        # Publish updates
        self.publish_update_to_parameter("extended_image", extended_artifact)
        self.publish_update_to_parameter("extension_mask", mask_artifact)

    def _calculate_position(
        self, 
        original_width: int, 
        original_height: int, 
        target_width: int, 
        target_height: int, 
        direction: str
    ) -> Tuple[int, int]:
        """Calculate the position to place the original image based on direction."""
        if direction == "center":
            x = (target_width - original_width) // 2
            y = (target_height - original_height) // 2
        elif direction == "top_left":
            x, y = 0, 0
        elif direction == "top_right":
            x = target_width - original_width
            y = 0
        elif direction == "bottom_left":
            x = 0
            y = target_height - original_height
        elif direction == "bottom_right":
            x = target_width - original_width
            y = target_height - original_height
        elif direction == "top":
            x = (target_width - original_width) // 2
            y = 0
        elif direction == "bottom":
            x = (target_width - original_width) // 2
            y = target_height - original_height
        elif direction == "left":
            x = 0
            y = (target_height - original_height) // 2
        elif direction == "right":
            x = target_width - original_width
            y = (target_height - original_height) // 2
        else:
            # Default to center
            x = (target_width - original_width) // 2
            y = (target_height - original_height) // 2

        return x, y 

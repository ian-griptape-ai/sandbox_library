"""
Extract Last Frame Node
Extracts the last frame from a video and outputs it as an ImageUrlArtifact.
"""
import os
import tempfile
import subprocess
from typing import Any

from griptape.artifacts import UrlArtifact, ImageUrlArtifact
from PIL import Image

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes_library.utils.image_utils import save_pil_image_to_static_file


class VideoUrlArtifact(UrlArtifact):
    """
    Artifact that contains a URL to a video.
    """
    def __init__(self, url: str, name: str | None = None):
        super().__init__(value=url, name=name or self.__class__.__name__)
        self.mime_type = "video/mp4"
        self.media_type = "video"


class ExtractLastFrame(DataNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.category = "Video"
        self.description = "Extract the last frame from a video and output as an image"
        
        # Input video parameter
        self.add_parameter(
            Parameter(
                name="video_input",
                input_types=["VideoUrlArtifact", "str"],
                type="VideoUrlArtifact",
                tooltip="Input video URL to extract last frame from",
                allowed_modes={ParameterMode.INPUT},
            )
        )
        
        # Output image parameter
        self.add_parameter(
            Parameter(
                name="last_frame_image",
                output_type="ImageUrlArtifact",
                type="ImageUrlArtifact",
                tooltip="The last frame extracted from the video as an image",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"expander": True}
            )
        )
    
    def process(self) -> None:
        """Extract the last frame from the input video."""
        video_input = self.get_parameter_value("video_input")
        
        if video_input is None:
            raise ValueError("No input video provided")
        
        # Handle different input types
        if isinstance(video_input, str):
            video_url = video_input
        elif isinstance(video_input, VideoUrlArtifact):
            video_url = video_input.value
        elif hasattr(video_input, 'value'):
            video_url = video_input.value
        else:
            raise ValueError("Invalid video input type")
        
        try:
            # Extract the last frame
            last_frame_pil = self._extract_last_frame_from_url(video_url)
            
            # Save as ImageUrlArtifact using utility function
            image_artifact = save_pil_image_to_static_file(last_frame_pil)
            
            # Set the output parameter
            self.parameter_output_values["last_frame_image"] = image_artifact
            
        except Exception as e:
            # Set safe default
            self.parameter_output_values["last_frame_image"] = None
            raise Exception(f"Error extracting last frame from video: {str(e)}")
    
    def _extract_last_frame_from_url(self, video_url: str) -> Image.Image:
        """
        Extract the last frame directly from video URL using ffmpeg.
        
        Args:
            video_url: URL of the video to process
            
        Returns:
            PIL Image of the last frame
        """
        # Create a temporary file for the output image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_image_path = temp_file.name
            
        try:
            # Extract last frame using ffmpeg directly from URL
            self._extract_last_frame_with_ffmpeg(video_url, temp_image_path)
            
            # Load the extracted frame as PIL Image
            last_frame_pil = Image.open(temp_image_path)
            
            return last_frame_pil
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
    
    def _extract_last_frame_with_ffmpeg(self, video_url: str, output_path: str) -> None:
        """
        Extract the last frame from a video URL using ffmpeg.
        
        Args:
            video_url: URL of the video to process
            output_path: Path where to save the extracted frame image
        """
        try:
            # Use ffmpeg to extract the last frame
            # -sseof -1: seek to 1 second before end of file (must come before -i)
            # -vframes 1: extract only 1 frame
            # -f image2: output as image format
            # -update 1: overwrite output file if it exists
            cmd = [
                "ffmpeg",
                "-sseof", "-1",            # Seek to 1 second before end (BEFORE input)
                "-i", video_url,           # Input video URL
                "-vframes", "1",           # Extract 1 frame
                "-f", "image2",            # Output as image
                "-update", "1",            # Overwrite existing file
                "-y",                      # Overwrite output file without asking
                output_path                # Output path
            ]
            
            # Run ffmpeg command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False   # Don't raise exception on non-zero exit
            )
            
            # Check if the command was successful
            if result.returncode != 0:
                raise ValueError(f"ffmpeg command failed with return code {result.returncode}: {result.stderr}")
            
            # Check if output file was created
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError("ffmpeg did not create output file or file is empty")
                
        except subprocess.TimeoutExpired:
            raise ValueError("ffmpeg command timed out after 5 minutes")
        except FileNotFoundError:
            raise ValueError(
                "ffmpeg not found. Please ensure ffmpeg is installed and available in PATH. "
                "Install instructions: https://ffmpeg.org/download.html"
            )
        except Exception as e:
            raise ValueError(f"Error extracting last frame with ffmpeg: {str(e)}")

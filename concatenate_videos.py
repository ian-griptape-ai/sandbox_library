"""
Video Concatenation Node
Concatenates multiple videos into a single video using ffmpeg.
"""
import os
import tempfile
import subprocess
import uuid
import json
from typing import List, Tuple

from griptape.artifacts import UrlArtifact

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode, ParameterList
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes


class VideoUrlArtifact(UrlArtifact):
    """
    Artifact that contains a URL to a video.
    """
    def __init__(self, url: str, name: str | None = None):
        super().__init__(value=url, name=name or self.__class__.__name__)
        self.mime_type = "video/mp4"
        self.media_type = "video"


class OldConcatenateVideos(DataNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        
        self.category = "Video"
        self.description = "Concatenate multiple videos into a single video file"
        
        # Input videos parameter using ParameterList pattern
        self.add_parameter(
            ParameterList(
                name="video_inputs",
                input_types=["VideoUrlArtifact", "list[VideoUrlArtifact]"],
                default_value=[],
                tooltip="Connect individual videos or a list of videos to concatenate",
                allowed_modes={ParameterMode.INPUT},
            )
        )
        
        # Video format parameter
        self.add_parameter(
            Parameter(
                name="output_format",
                input_types=["str"],
                type="str",
                tooltip="Output video format",
                default_value="mp4",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"placeholder_text": "mp4, avi, mov, etc."}
            )
        )
        
        # Video codec parameter
        self.add_parameter(
            Parameter(
                name="video_codec",
                input_types=["str"],
                type="str",
                tooltip="Video codec for output",
                default_value="libx264",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"placeholder_text": "libx264, libx265, copy"}
            )
        )
        
        # Status parameter for progress feedback
        self.add_parameter(
            Parameter(
                name="status",
                output_type="str",
                type="str",
                tooltip="Processing status",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"hide": True}
            )
        )
        
        # Output concatenated video parameter
        self.add_parameter(
            Parameter(
                name="concatenated_video",
                output_type="VideoUrlArtifact",
                type="VideoUrlArtifact",
                tooltip="The concatenated video file",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"expander": True}
            )
        )
    
    def process(self) -> None:
        """Concatenate the input videos using ffmpeg."""
        # Get the list of video inputs
        video_inputs = self.get_parameter_list_value("video_inputs")
        
        if not video_inputs:
            self.parameter_output_values["status"] = "❌ No video inputs provided"
            self.parameter_output_values["concatenated_video"] = None
            raise ValueError("No video inputs provided for concatenation")
        
        if len(video_inputs) < 2:
            self.parameter_output_values["status"] = "❌ At least 2 videos required for concatenation"
            self.parameter_output_values["concatenated_video"] = None
            raise ValueError("At least 2 videos are required for concatenation")
        
        # Get processing parameters
        output_format = self.get_parameter_value("output_format")
        video_codec = self.get_parameter_value("video_codec")
        
        try:
            self.publish_update_to_parameter("status", f"🔄 Processing {len(video_inputs)} videos...")
            
            # Extract video URLs
            video_urls = []
            for video_input in video_inputs:
                if isinstance(video_input, str):
                    video_urls.append(video_input)
                elif isinstance(video_input, VideoUrlArtifact):
                    video_urls.append(video_input.value)
                elif hasattr(video_input, 'value'):
                    video_urls.append(video_input.value)
                else:
                    raise ValueError(f"Invalid video input type: {type(video_input)}")
            
            # Concatenate the videos
            concatenated_video_artifact, resize_operations = self._concatenate_videos_with_ffmpeg(
                video_urls, output_format, video_codec
            )
            
            # Build final status message with resize information
            final_status = f"✅ Successfully concatenated {len(video_inputs)} videos"
            if resize_operations:
                final_status += "\n\n🔄 Video Processing Details:\n" + "\n".join(resize_operations)
            
            # Set the output parameters
            self.parameter_output_values["concatenated_video"] = concatenated_video_artifact
            self.parameter_output_values["status"] = final_status
            
            # Publish updates to UI
            self.publish_update_to_parameter("concatenated_video", concatenated_video_artifact)
            self.publish_update_to_parameter("status", final_status)
            
        except Exception as e:
            # Set safe defaults
            self.parameter_output_values["concatenated_video"] = None
            error_msg = f"❌ Error concatenating videos: {str(e)}"
            self.parameter_output_values["status"] = error_msg
            self.publish_update_to_parameter("status", error_msg)
            raise Exception(f"Error concatenating videos: {str(e)}")
    
    def _concatenate_videos_with_ffmpeg(
        self, 
        video_urls: List[str], 
        output_format: str,
        video_codec: str
    ) -> Tuple[VideoUrlArtifact, List[str]]:
        """
        Concatenate videos using ffmpeg.
        
        Args:
            video_urls: List of video URLs to concatenate
            output_format: Output format (e.g., 'mp4', 'avi')
            video_codec: Video codec (e.g., 'libx264', 'libx265')
            
        Returns:
            Tuple of (VideoUrlArtifact of the concatenated video, List of resize operation messages)
        """
        # Create temporary files for processing
        temp_files = []
        concat_list_file = None
        output_file = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Generate unique filename for output
            output_filename = f"concatenated_video_{uuid.uuid4()}.{output_format}"
            output_file = os.path.join(temp_dir, output_filename)
            
            # Create concat list file for ffmpeg
            concat_list_file = os.path.join(temp_dir, f"concat_list_{uuid.uuid4()}.txt")
            
            # Download videos first
            downloaded_videos = []
            for i, video_url in enumerate(video_urls):
                # Create temporary file for each video
                temp_video_file = os.path.join(temp_dir, f"video_original_{i}_{uuid.uuid4()}.mp4")
                temp_files.append(temp_video_file)
                
                # Download video to temp file
                self._download_video(video_url, temp_video_file)
                downloaded_videos.append(temp_video_file)
            
            self.publish_update_to_parameter("status", "🔄 Checking video dimensions...")
            
            # Get dimensions of all videos
            video_dimensions = []
            for video_file in downloaded_videos:
                dimensions = self._get_video_dimensions(video_file)
                video_dimensions.append(dimensions)
            
            # Use first video's dimensions as target
            target_width, target_height = video_dimensions[0]
            
            # Check if all videos have the same dimensions
            all_same_size = all(dims == (target_width, target_height) for dims in video_dimensions)
            
            # Prepare status messages for resizing operations
            resize_operations = []
            
            # Process videos for concatenation (resize if needed)
            processed_videos = []
            if all_same_size:
                # All videos are the same size, use original files
                processed_videos = downloaded_videos
                resize_operations.append("✅ All videos have matching dimensions - no resizing needed")
                self.publish_update_to_parameter("status", "✅ All videos match dimensions - proceeding with concatenation...")
            else:
                # Some videos need resizing
                self.publish_update_to_parameter("status", "🔄 Resizing videos to match first video dimensions...")
                
                for i, (video_file, dimensions) in enumerate(zip(downloaded_videos, video_dimensions)):
                    if i == 0:
                        # First video is the target, use as-is
                        processed_videos.append(video_file)
                        resize_operations.append(f"• Video 1: {dimensions[0]}x{dimensions[1]} (reference)")
                    else:
                        # Check if this video needs resizing
                        if dimensions == (target_width, target_height):
                            # Same size as target, use as-is
                            processed_videos.append(video_file)
                            resize_operations.append(f"• Video {i+1}: {dimensions[0]}x{dimensions[1]} (no resize needed)")
                        else:
                            # Resize this video
                            resized_video_file = os.path.join(temp_dir, f"video_resized_{i}_{uuid.uuid4()}.mp4")
                            temp_files.append(resized_video_file)
                            
                            self._resize_video(video_file, resized_video_file, target_width, target_height)
                            processed_videos.append(resized_video_file)
                            resize_operations.append(f"• Video {i+1}: {dimensions[0]}x{dimensions[1]} → {target_width}x{target_height} (resized)")
            
            # Create concat list with processed videos
            with open(concat_list_file, 'w') as f:
                for video_file in processed_videos:
                    # Add to concat list (escape the path for ffmpeg)
                    escaped_path = video_file.replace("'", "'\"'\"'")
                    f.write(f"file '{escaped_path}'\n")
            
            # Build ffmpeg command for concatenation
            cmd = [
                "ffmpeg",
                "-f", "concat",           # Use concat demuxer
                "-safe", "0",             # Allow unsafe file names
                "-i", concat_list_file,   # Input concat list file
                "-c:v", video_codec,      # Video codec
                "-c:a", "aac",            # Audio codec
                "-strict", "experimental", # Allow experimental codecs
                "-y",                     # Overwrite output file
                output_file               # Output file
            ]
            
            self.publish_update_to_parameter("status", "🔄 Running ffmpeg concatenation...")
            
            # Run ffmpeg command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                check=False
            )
            
            # Check if the command was successful
            if result.returncode != 0:
                raise ValueError(f"ffmpeg command failed with return code {result.returncode}: {result.stderr}")
            
            # Check if output file was created
            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                raise ValueError("ffmpeg did not create output file or file is empty")
            
            self.publish_update_to_parameter("status", "🔄 Saving concatenated video...")
            
            # Save the concatenated video to static files
            video_artifact = self._save_video_to_static_file(output_file, output_filename)
            
            return video_artifact, resize_operations
            
        except subprocess.TimeoutExpired:
            raise ValueError("ffmpeg command timed out after 10 minutes")
        except FileNotFoundError:
            raise ValueError(
                "ffmpeg not found. Please ensure ffmpeg is installed and available in PATH. "
                "Install instructions: https://ffmpeg.org/download.html"
            )
        except Exception as e:
            raise ValueError(f"Error during video concatenation: {str(e)}")
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.unlink(temp_file)
                    except OSError:
                        pass  # Ignore cleanup errors
            
            if concat_list_file and os.path.exists(concat_list_file):
                try:
                    os.unlink(concat_list_file)
                except OSError:
                    pass
                    
            if output_file and os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except OSError:
                    pass
    
    def _get_video_dimensions(self, video_path: str) -> Tuple[int, int]:
        """
        Get video dimensions using ffprobe.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Tuple of (width, height)
        """
        try:
            # Use ffprobe to get video information
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-select_streams", "v:0",  # Select first video stream
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )
            
            if result.returncode != 0:
                raise ValueError(f"ffprobe command failed: {result.stderr}")
            
            # Parse JSON output
            probe_data = json.loads(result.stdout)
            
            # Get video stream information
            if not probe_data.get("streams"):
                raise ValueError("No video streams found in file")
            
            video_stream = probe_data["streams"][0]
            width = int(video_stream["width"])
            height = int(video_stream["height"])
            
            return (width, height)
            
        except subprocess.TimeoutExpired:
            raise ValueError("ffprobe command timed out")
        except FileNotFoundError:
            raise ValueError(
                "ffprobe not found. Please ensure ffmpeg is installed and available in PATH. "
                "Install instructions: https://ffmpeg.org/download.html"
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Error parsing video information: {str(e)}")
    
    def _resize_video(self, input_path: str, output_path: str, target_width: int, target_height: int) -> None:
        """
        Resize a video to target dimensions using ffmpeg.
        
        Args:
            input_path: Path to the input video
            output_path: Path for the resized output video
            target_width: Target width in pixels
            target_height: Target height in pixels
        """
        try:
            # Build ffmpeg command for resizing
            # Use scale filter with force_original_aspect_ratio=decrease to maintain aspect ratio
            # and pad with black bars if needed to reach exact target dimensions
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2:black",
                "-c:a", "copy",  # Copy audio without re-encoding
                "-y",  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout for resizing
                check=False
            )
            
            if result.returncode != 0:
                raise ValueError(f"ffmpeg resize command failed: {result.stderr}")
            
            # Check if output file was created
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError("ffmpeg did not create resized video file or file is empty")
                
        except subprocess.TimeoutExpired:
            raise ValueError("ffmpeg resize command timed out")
        except FileNotFoundError:
            raise ValueError(
                "ffmpeg not found. Please ensure ffmpeg is installed and available in PATH. "
                "Install instructions: https://ffmpeg.org/download.html"
            )
        except Exception as e:
            raise ValueError(f"Error resizing video: {str(e)}")
    
    def _download_video(self, video_url: str, output_path: str) -> None:
        """
        Download a video from URL to local file.
        
        Args:
            video_url: URL of the video to download
            output_path: Path where to save the video
        """
        try:
            # Use requests to download the video
            import requests
            
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was downloaded
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise ValueError("Downloaded video file is empty or does not exist")
                
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error downloading video from {video_url}: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error saving video to {output_path}: {str(e)}")
    
    def _save_video_to_static_file(self, video_file_path: str, filename: str) -> VideoUrlArtifact:
        """
        Save a video file to static file storage and return VideoUrlArtifact.
        
        Args:
            video_file_path: Path to the video file
            filename: Desired filename for the artifact
            
        Returns:
            VideoUrlArtifact pointing to the saved video
        """
        try:
            # Read the video file
            with open(video_file_path, 'rb') as f:
                video_data = f.read()
            
            # Save to static file using StaticFilesManager
            static_url = GriptapeNodes.StaticFilesManager().save_static_file(video_data, filename)
            
            # Create and return VideoUrlArtifact
            return VideoUrlArtifact(static_url, name=f"Concatenated Video ({filename})")
            
        except Exception as e:
            raise ValueError(f"Error saving video to static file: {str(e)}")

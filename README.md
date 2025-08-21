# Sandbox Library

Custom Griptape nodes for video and audio processing.

## Nodes

### ExtractLastFrame

Extracts the last frame from a video and outputs it as an ImageUrlArtifact.

**Category:** Video Processing  
**Input:** VideoUrlArtifact or video URL string  
**Output:** ImageUrlArtifact (last frame as image)

**Usage:**
1. Connect a video URL artifact or provide a video URL string
2. Run the node to extract the last frame
3. The output will be an image artifact of the last frame

**Dependencies:**
- ffmpeg (system dependency for video processing)
- Pillow (for image handling)

**Features:**
- Processes video URLs directly without downloading
- Uses ffmpeg for efficient and reliable frame extraction
- Automatically cleans up temporary files
- Robust error handling with clear error messages

## Installation

The dependencies will be automatically installed when the library is loaded by the Griptape Nodes engine.

## Development

This library follows the Griptape Node Development Guide v2 patterns and conventions.

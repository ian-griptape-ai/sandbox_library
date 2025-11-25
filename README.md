# Sandbox Library

Custom Griptape nodes for video, audio, and image processing.

## Nodes

### GaussianEdgeFade

Applies Gaussian-blurred alpha channel fade to image edges for smooth compositing over other images.

**Category:** Image  
**Input:** ImageArtifact or ImageUrlArtifact  
**Output:** ImageUrlArtifact (image with alpha channel edge fade)

**Parameters:**
- **fade_mode**: Choose between "percentage" (relative to image size) or "pixels" (absolute distance)
- **fade_distance**: How far from the edge to fade (default: 5)
- **blur_radius**: Gaussian blur strength for smooth transitions (0-100, default: 10)
- **fade_curve**: Shape of transparency transition (0.5-4.0, default: 2.0)
  - 1.0 = linear fade
  - >1.0 = more transparent near edges (aggressive fade)
  - <1.0 = less transparent near edges (gentle fade)
- **edge_shape**: Fade geometry - "square" (straight edges) or "rounded" (curved corners)
- **replace_mask**: Control alpha channel handling (default: False)
  - False = Combines edge fade with existing alpha channel (preserves transparency)
  - True = Replaces existing alpha channel entirely with edge fade
- **apply_top/bottom/left/right**: Individual toggles for each edge

**Usage:**
1. Connect an image artifact or provide an image URL
2. Configure fade parameters:
   - Select percentage mode for resolution-independent fading
   - Select pixel mode for precise control
3. Adjust blur radius for softer or sharper transitions
4. Choose which edges to apply the fade to
5. Run the node to generate the output with alpha channel fade

**Use Cases:**
- Seamlessly composite images together with smooth edge transitions
- Create vignette-style edge fading
- Prepare images for overlay on varied backgrounds
- Generate masks for gradual image blending
- Add edge fading to images that already have transparency
- Replace existing alpha channels with new edge fades

**Dependencies:**
- Pillow (PIL) for image processing
- NumPy for efficient gradient calculations
- griptape_nodes_library.utils for image handling

**Features:**
- Flexible edge control (all edges or selective)
- Two measurement modes (percentage and pixels)
- Two fade shapes (square with straight edges, rounded with curved corners)
- Configurable Gaussian blur for smooth transitions
- Power curve control for aggressive or gentle transparency
- Automatic alpha channel handling
- Preserves image quality and format

---

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

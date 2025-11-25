# GaussianEdgeFade Node - Usage Examples

## Overview

The GaussianEdgeFade node applies a Gaussian-blurred alpha channel mask to image edges, creating smooth transitions for seamless compositing.

## Basic Usage

### Example 1: Rounded Fade with Curved Corners (Modern Look)

**Scenario:** Create an organic vignette with smooth, rounded corners

**Configuration:**
- **input_image**: Your source image
- **fade_mode**: "percentage"
- **fade_distance**: 10.0 (10% of image dimension)
- **blur_radius**: 15.0
- **fade_curve**: 2.0 (stays more transparent near edges)
- **edge_shape**: "rounded"
- **replace_mask**: False (preserves any existing transparency)
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Image with soft, rounded fade that creates natural-looking curved corners ideal for modern UI designs

---

### Example 2: Square Fade with Straight Edges (Classic Look)

**Scenario:** Traditional vignette with straight, independent edge fades

**Configuration:**
- **input_image**: Your source image
- **fade_mode**: "percentage"
- **fade_distance**: 10.0 (10% of image dimension)
- **blur_radius**: 15.0
- **fade_curve**: 2.0
- **edge_shape**: "square"
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Image with traditional square vignette where edges fade independently

---

### Example 3: Letterbox-Style with Square Edges

**Scenario:** Create a letterbox-style fade for video thumbnail overlay

**Configuration:**
- **input_image**: Your source image
- **fade_mode**: "pixels"
- **fade_distance**: 50.0 (50 pixels from edge)
- **blur_radius**: 20.0
- **fade_curve**: 2.0
- **edge_shape**: "square"
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: False
- **apply_right**: False

**Result:** Image with horizontal fades only, suitable for widescreen overlays

---

### Example 4: Subtle Rounded Blend for Photo Compositing

**Scenario:** Prepare a portrait for compositing with organic edge transitions

**Configuration:**
- **input_image**: Portrait photo
- **fade_mode**: "percentage"
- **fade_distance**: 5.0 (5% of image dimension)
- **blur_radius**: 25.0 (high blur for very soft transition)
- **fade_curve**: 2.5 (very aggressive - maximum transparency at edges)
- **edge_shape**: "rounded"
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Portrait with imperceptible rounded edge fade for natural compositing

---

### Example 5: Sharp Square Edge Mask

**Scenario:** Create a precise mask with minimal blur

**Configuration:**
- **input_image**: Product photo
- **fade_mode**: "pixels"
- **fade_distance**: 30.0
- **blur_radius**: 5.0 (low blur for sharper transition)
- **fade_curve**: 1.0 (linear transition)
- **edge_shape**: "square"
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Product image with defined but smooth square edge mask

---

### Example 6: Gentle Rounded Fade for Overlay Text

**Scenario:** Soften edges with rounded corners for UI elements

**Configuration:**
- **input_image**: Text overlay image
- **fade_mode**: "pixels"
- **fade_distance**: 20.0
- **blur_radius**: 10.0
- **fade_curve**: 0.7 (gentle curve - less transparency at edges)
- **edge_shape**: "rounded"
- **replace_mask**: False
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Text with gentle rounded edge softening that remains mostly opaque

---

### Example 7: Preserve Existing Transparency

**Scenario:** Add edge fade to an image that already has cutout/transparent areas

**Configuration:**
- **input_image**: PNG with existing transparency (e.g., logo with transparent background)
- **fade_mode**: "percentage"
- **fade_distance**: 8.0
- **blur_radius**: 12.0
- **fade_curve**: 2.0
- **edge_shape**: "rounded"
- **replace_mask**: False (combines with existing alpha)
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Logo keeps its transparent cutouts while adding smooth edge fade

---

### Example 8: Replace Existing Alpha with New Fade

**Scenario:** Image has unwanted transparency, replace it entirely with clean edge fade

**Configuration:**
- **input_image**: Image with messy or partial transparency
- **fade_mode**: "percentage"
- **fade_distance**: 10.0
- **blur_radius**: 15.0
- **fade_curve**: 2.0
- **edge_shape**: "rounded"
- **replace_mask**: True (ignores existing alpha channel)
- **apply_top**: True
- **apply_bottom**: True
- **apply_left**: True
- **apply_right**: True

**Result:** Clean, uniform edge fade ignoring any previous transparency

---

## Parameter Guide

### Fade Mode

**Percentage Mode:**
- Best for: Resolution-independent effects
- Value range: 0-50% of image dimension
- Use when: Working with images of varying sizes
- Example: 10% fade looks consistent across 800px and 4000px images

**Pixel Mode:**
- Best for: Precise, fixed-size fades
- Value range: 0-500 pixels
- Use when: You need exact pixel control
- Example: 50px fade for specific layout requirements

### Blur Radius

- **0-5**: Sharp transitions with visible gradient steps
- **5-15**: Moderate smoothing, good for most uses (default: 10)
- **15-30**: Soft, gradual transitions
- **30-100**: Very soft, subtle fades

### Edge Shape

Controls the geometry of the fade:

**Square (Default for Technical Work):**
- Each edge fades independently
- Creates straight edge transitions
- Corners are formed by overlapping edge fades
- Best for: Traditional vignettes, letterbox effects, technical masking
- Faster processing

**Rounded (Recommended for Organic Look):**
- Fade follows curved corner transitions
- Creates smooth, rounded rectangle shape
- Uses distance field calculation for organic appearance
- Best for: Modern UI, photo compositing, natural-looking fades
- Slightly slower but more visually appealing

### Fade Curve

The fade curve controls how transparency transitions from edge to center:

- **0.5-0.9**: Gentle curve - edges stay MORE opaque, quick transition to full opacity
  - Use for: Text overlays, logos, when you want visible edges
  
- **1.0**: Linear - even transition from transparent to opaque
  - Use for: Technical/mechanical fades, traditional vignettes
  
- **1.5-2.5**: Aggressive curve - edges stay MORE transparent, gradual transition to opacity (default: 2.0)
  - Use for: Natural compositing, blending images seamlessly
  - **Recommended for most use cases**
  
- **3.0-4.0**: Very aggressive - extreme transparency at edges, very gradual fade
  - Use for: Maximum edge transparency, ultra-smooth blends

**Visual Guide:**
- Fade curve 0.7: Edge at 10% → Mid at 50% → Center at 100%
- Fade curve 1.0: Edge at 10% → Mid at 30% → Center at 100%
- Fade curve 2.0: Edge at 1% → Mid at 10% → Center at 100% ← **Default**
- Fade curve 3.0: Edge at 0.1% → Mid at 5% → Center at 100%

### Replace Mask

Controls how the edge fade interacts with existing alpha channels:

**False (Default - Preserve & Combine):**
- Preserves any existing transparency in the input image
- Multiplies existing alpha channel with new edge fade mask
- Example: Logo with transparent background keeps cutouts while adding edge fade
- Example: PNG with partial transparency combines both transparencies
- Use when: Working with images that already have meaningful transparency

**True (Replace Entirely):**
- Ignores any existing alpha channel in the input image
- Replaces it completely with the new edge fade
- Example: Image with messy transparency gets clean edge fade
- Example: Opaque image gets fresh alpha channel
- Use when: You want to discard existing transparency or start fresh

**Technical Note:** When replace_mask is False, the alpha values are multiplied:
```
Final Alpha = (Original Alpha / 255) × (Edge Fade Alpha / 255) × 255
```
This means areas that were already transparent stay transparent, and the edge fade is applied on top.

### Edge Selection Strategy

**All Edges:**
- Uniform vignette effect
- Centered subject emphasis
- General-purpose compositing
- Rounded shape creates organic rounded rectangle
- Square shape creates traditional vignette

**Selective Edges:**
- Top/Bottom only: Letterbox or cinematic effect (use square shape)
- Left/Right only: Portrait frame effect (use square shape)
- Single edge: Directional fade for specific compositions
- Note: Rounded shape still curves corners even with selective edges

---

## Workflow Integration Tips

1. **Before Image-to-Video Generation:**
   - Apply edge fade to static images before converting to video
   - Creates more professional-looking transitions

2. **Multi-Layer Compositing:**
   - Chain multiple GaussianEdgeFade nodes with different images
   - Layer them in image compositing nodes
   - Build complex, multi-layered compositions

3. **Batch Processing:**
   - Use consistent percentage-based settings across multiple images
   - Ensures uniform appearance regardless of source image size

4. **Quality Optimization:**
   - Higher blur radius = smoother results but slower processing
   - Percentage mode recommended for automated workflows
   - Pixel mode recommended for precise design requirements

---

## Technical Notes

- **Output Format:** RGBA PNG with alpha channel preserved
- **Input Requirements:** Any image format supported by PIL
- **Processing:** Non-destructive; original image data preserved in non-faded areas
- **Alpha Compositing:** Uses multiplicative alpha blending for gradual opacity
- **Edge Handling:** Automatically clamps fade distance to prevent artifacts

---

## Common Issues and Solutions

**Issue:** Edges not transparent enough
- **Solution:** Increase fade_curve value (try 2.5 or 3.0 for more aggressive transparency)

**Issue:** Edges too transparent / disappearing
- **Solution:** Decrease fade_curve value (try 1.0 or 0.7 for gentler fade)

**Issue:** Fade appears too harsh
- **Solution:** Increase blur_radius for smoother transition

**Issue:** Fade doesn't reach far enough into image
- **Solution:** Increase fade_distance value

**Issue:** Different results on different image sizes
- **Solution:** Use "percentage" mode instead of "pixels"

**Issue:** Output image has black edges instead of transparency
- **Solution:** Ensure your downstream nodes support RGBA/alpha channels

**Issue:** Linear fade looks unnatural
- **Solution:** Use fade_curve > 1.0 (default 2.0 gives natural-looking results)

**Issue:** Corners look harsh or squared off
- **Solution:** Use edge_shape "rounded" for smooth, curved corner transitions

**Issue:** Want traditional vignette with straight edges
- **Solution:** Use edge_shape "square" for independent edge fading

**Issue:** Existing transparency in image is being lost
- **Solution:** Set replace_mask to False (default) to preserve existing alpha channel

**Issue:** Image has unwanted transparency that interferes with fade
- **Solution:** Set replace_mask to True to replace existing alpha entirely

**Issue:** Logo cutouts are disappearing when adding edge fade
- **Solution:** Ensure replace_mask is False to combine edge fade with existing transparency


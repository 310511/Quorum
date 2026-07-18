# CooperBench pair: pair_07_huggingface_datasets_t6252_f3v5

- **Repo:** huggingface/datasets
- **Base commit:** 0b55ec53e980855d71ae22f8b3d12b2a0d476a51
- **CooperBench label:** conflict

## Feature A (branch_a): Add Optional Image Size Clamping with Max Resolution Threshold

**Title**: Add Optional Image Size Clamping with Max Resolution Threshold

**Pull Request Details**

**Description**:
Introduces an optional `max_resolution` parameter to the `Image` feature, which clamps image dimensions during decoding. If an image exceeds the specified width or height, it is downscaled proportionally to fit within the limit while maintaining aspect ratio.

**Technical Background**:
**Problem**:
High-resolution images can consume excessive memory and slow down preprocessing, especially in large-scale training pipelines. Users currently have to manually resize such images after decoding.

**Solution**:
The new `max_resolution` parameter enables automatic downscaling of images during `decode_example`. If either dimension exceeds the threshold, the image is resized using Pillow's `thumbnail()` method to fit within the specified bounds.

**Files Modified**
- `src/datasets/features/image.py`

## Feature B (branch_b): Add Option to Normalize Image Pixels to Float32 NumPy Array

**Title**: Add Option to Normalize Image Pixels to Float32 NumPy Array

**Pull Request Details**

**Description**:
Introduces support for normalizing image pixel values by converting them into a `float32` NumPy array scaled to the range [0, 1], controlled by a new `as_array` flag in the `Image` feature. This enables users to directly work with NumPy arrays in downstream pipelines without relying on PIL post-processing.

**Technical Background**:
**Problem**:
Many machine learning workflows operate directly on NumPy arrays with normalized pixel values. Currently, images are returned as PIL Images, requiring extra conversion steps that may introduce performance overhead or inconsistency in preprocessing pipelines.

**Solution**:
When `Image(as_array=True)` is used, decoded images are automatically converted to NumPy arrays of `dtype=float32` and scaled to [0, 1]. This simplifies integration with NumPy-based pipelines and enables consistent preprocessing across datasets.

**Files Modified**
- `src/datasets/features/image.py`

## Files touched
src/datasets/features/image.py, tests/features/test_image.py

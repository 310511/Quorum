import pytest

from PIL import Image

from .helper import assert_image, assert_image_similar, hopper, is_ppc64le


def test_sanity():
    image = hopper()
    converted = image.quantize()
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 10)

    image = hopper()
    converted = image.quantize(palette=hopper("P"))
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 60)


@pytest.mark.xfail(is_ppc64le(), reason="failing on ppc64le on GHA")
def test_libimagequant_quantize():
    image = hopper()
    try:
        converted = image.quantize(100, Image.LIBIMAGEQUANT)
    except ValueError as ex:  # pragma: no cover
        if "dependency" in str(ex).lower():
            pytest.skip("libimagequant support not available")
        else:
            raise
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 15)
    assert len(converted.getcolors()) == 100


def test_octree_quantize():
    image = hopper()
    converted = image.quantize(100, Image.FASTOCTREE)
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 20)
    assert len(converted.getcolors()) == 100


def test_rgba_quantize():
    image = hopper("RGBA")
    with pytest.raises(ValueError):
        image.quantize(method=0)

    assert image.quantize().convert().mode == "RGBA"


def test_quantize():
    with Image.open("Tests/images/caption_6_33_22.png") as image:
        image = image.convert("RGB")
    converted = image.quantize()
    assert_image(converted, "P", converted.size)
    assert_image_similar(converted.convert("RGB"), image, 1)


def test_quantize_no_dither():
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    converted = image.quantize(dither=0, palette=palette)
    assert_image(converted, "P", converted.size)
    assert converted.palette.palette == palette.palette.palette


def test_quantize_dither_diff():
    image = hopper()
    with Image.open("Tests/images/caption_6_33_22.png") as palette:
        palette = palette.convert("P")

    dither = image.quantize(dither=1, palette=palette)
    nodither = image.quantize(dither=0, palette=palette)

    assert dither.tobytes() != nodither.tobytes()


def test_transparent_colors_equal():
    im = Image.new("RGBA", (1, 2), (0, 0, 0, 0))
    px = im.load()
    px[0, 1] = (255, 255, 255, 0)

    converted = im.quantize()
    converted_px = converted.load()
    assert converted_px[0, 0] == converted_px[0, 1]

import numpy as np

def test_lightness_factor_quantize() -> None:
    """Test that lightness_factor properly adjusts brightness after quantization."""
    image = hopper()
 
    # Standard quantization
    standard = image.quantize(64)
    standard_rgb = standard.convert("RGB")
 
    # Lightened quantization (10% brighter)
    lightened = image.quantize(64, lightness_factor=1.1)
    lightened_rgb = lightened.convert("RGB")
 
    # Darkened quantization (10% darker)
    darkened = image.quantize(64, lightness_factor=0.9)
    darkened_rgb = darkened.convert("RGB")
 
    # Calculate average brightness of each result
    standard_array = np.array(standard_rgb)
    lightened_array = np.array(lightened_rgb)
    darkened_array = np.array(darkened_rgb)
 
    standard_brightness = np.mean(standard_array)
    lightened_brightness = np.mean(lightened_array)
    darkened_brightness = np.mean(darkened_array)
 
    # Lightened should be brighter than standard
    assert lightened_brightness > standard_brightness
 
    # Darkened should be darker than standard
    assert darkened_brightness < standard_brightness
 
    # Check that the brightness change is approximately correct (accounting for clamping)
    # Should be roughly 10% different, but with some margin for clamping effects
    expected_light_increase = standard_brightness * 0.1
    actual_light_increase = lightened_brightness - standard_brightness
    assert actual_light_increase > 0
    assert abs(actual_light_increase - expected_light_increase) / expected_light_increase < 0.5
 
    expected_dark_decrease = standard_brightness * 0.1
    actual_dark_decrease = standard_brightness - darkened_brightness
    assert actual_dark_decrease > 0
    assert abs(actual_dark_decrease - expected_dark_decrease) / expected_dark_decrease < 0.5


def test_lightness_factor_extreme_values() -> None:
    """Test extreme values of lightness_factor."""
    image = hopper()
 
    # Very bright (but values should still be clamped to 255)
    very_bright = image.quantize(64, lightness_factor=2.0)
 
    # Very dark (but values should still be non-negative)
    very_dark = image.quantize(64, lightness_factor=0.1)
 
    # Check that no values exceed valid ranges
    palette = very_bright.getpalette()
    assert palette is not None
    assert all(0 <= v <= 255 for v in palette)
 
    palette = very_dark.getpalette()
    assert palette is not None
    assert all(0 <= v <= 255 for v in palette)
 
    # Test invalid lightness factor
    with pytest.raises(ValueError):
        image.quantize(64, lightness_factor=-0.5)
 
    with pytest.raises(ValueError):
        image.quantize(64, lightness_factor=0)
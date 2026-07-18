import pytest
import tiktoken

def test_token_limit():
    # Create a simple encoding for testing
    enc = tiktoken.get_encoding("cl100k_base")
 
    # Test with no limit (should work)
    tokens = enc.encode("I love you so much that I want to marry you")
    assert len(tokens) == 11
 
    # Test with limit higher than token count (should work)
    tokens = enc.encode("I love you so much that I want to marry you", max_tokens=11)
    assert len(tokens) == 11
 
    # Test with limit lower than token count (should raise error)
    with pytest.raises(ValueError):
        enc.encode("I love you so much that I want to marry you", max_tokens=10)
 
    # Test with limit of 0 (should raise error)
    with pytest.raises(ValueError):
        enc.encode("Love you", max_tokens=0)
 
    # Test with negative limit (should raise ValueError)
    with pytest.raises(ValueError):
        enc.encode("Love you", max_tokens=-1)
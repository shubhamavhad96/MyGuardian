import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.validation import validate_request, MAX_PASSAGES, MAX_PASSAGE_SIZE_BYTES, MAX_TOTAL_SIZE_BYTES
from fastapi import HTTPException

client = TestClient(app)


def test_max_passages_limit():
    passages = [{"id": f"p{i}", "text": "test"} for i in range(MAX_PASSAGES + 1)]
    
    with pytest.raises(HTTPException) as exc_info:
        validate_request(passages, "question", "answer")
    assert exc_info.value.status_code == 413
    assert "Too many passages" in exc_info.value.detail


def test_max_passage_size_limit():
    large_text = "x" * (MAX_PASSAGE_SIZE_BYTES + 1)
    passages = [{"id": "p1", "text": large_text}]
    
    with pytest.raises(HTTPException) as exc_info:
        validate_request(passages, "question", "answer")
    assert exc_info.value.status_code == 413
    assert "exceeds size limit" in exc_info.value.detail


def test_max_total_size_limit():
    passage_size = MAX_PASSAGE_SIZE_BYTES // 2
    num_passages = (MAX_TOTAL_SIZE_BYTES // passage_size) + 2
    passages = [{"id": f"p{i}", "text": "x" * passage_size} for i in range(num_passages)]
    
    with pytest.raises(HTTPException) as exc_info:
        validate_request(passages, "question", "answer")
    assert exc_info.value.status_code == 413
    assert "Total request size exceeds limit" in exc_info.value.detail


def test_valid_limits():
    passages = [{"id": f"p{i}", "text": "test"} for i in range(10)]
    validate_request(passages, "question", "answer")


def test_api_max_passages():
    passages = [{"id": f"p{i}", "text": "test"} for i in range(MAX_PASSAGES + 1)]
    response = client.post(
        "/evaluate",
        json={
            "question": "test",
            "answer": "test",
            "passages": passages
        },
        headers={"X-API-Key": "demo-key-change-in-production"}
    )
    assert response.status_code == 413


def test_api_max_passage_size():
    large_text = "x" * (MAX_PASSAGE_SIZE_BYTES + 1)
    response = client.post(
        "/evaluate",
        json={
            "question": "test",
            "answer": "test",
            "passages": [{"id": "p1", "text": large_text}]
        },
        headers={"X-API-Key": "demo-key-change-in-production"}
    )
    assert response.status_code == 413


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


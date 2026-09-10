"""
Unit tests for deterministic stable ID generation and collision handling.
"""

from app.intelligence.schemas import ContentType, generate_stable_knowledge_id


def test_same_normalized_input_produces_same_id():
    id1 = generate_stable_knowledge_id("doc_physics", "Titik nyala adalah suhu terendah...", ContentType.DEFINITION)
    id2 = generate_stable_knowledge_id("doc_physics", "Titik nyala adalah suhu terendah...", ContentType.DEFINITION)
    assert id1 == id2


def test_formatting_only_difference_produces_same_id():
    text1 = "  Titik Nyala adalah suhu TERENDAH... \n "
    text2 = "titik nyala adalah suhu terendah..."
    id1 = generate_stable_knowledge_id("doc_physics", text1, ContentType.DEFINITION)
    id2 = generate_stable_knowledge_id("doc_physics", text2, ContentType.DEFINITION)
    assert id1 == id2


def test_semantic_change_produces_different_id():
    text1 = "Titik nyala adalah suhu terendah..."
    text2 = "Titik didih adalah suhu saat tekanan uap jenuh..."
    id1 = generate_stable_knowledge_id("doc_physics", text1, ContentType.DEFINITION)
    id2 = generate_stable_knowledge_id("doc_physics", text2, ContentType.DEFINITION)
    assert id1 != id2


def test_id_format_prefix():
    ku_id = generate_stable_knowledge_id("doc_1", "Test content", ContentType.CONCEPT)
    assert ku_id.startswith("ku_")
    assert len(ku_id) == 15  # ku_ (3) + 12 hex chars = 15 chars

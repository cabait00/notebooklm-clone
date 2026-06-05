from app.services.chunking import chunk_text


def test_single_chunk_when_text_fits():
    chunks = chunk_text("Short text.", "doc1", "test.txt", "txt", chunk_size=100, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0].text == "Short text."


def test_multiple_chunks_produced_for_long_text():
    # 100 chars, size=60, overlap=20 → step=40 → 2 chunks: [0:60] and [40:100]
    text = "A" * 100
    chunks = chunk_text(text, "doc1", "test.txt", "txt", chunk_size=60, chunk_overlap=20)
    assert len(chunks) == 2


def test_overlap_content_is_shared():
    # Overlap region must appear at the end of chunk N and start of chunk N+1
    text = "A" * 100
    chunks = chunk_text(text, "doc1", "test.txt", "txt", chunk_size=60, chunk_overlap=20)
    # chunk[0] = text[0:60], chunk[1] = text[40:100]
    # Overlapping region is text[40:60] — last 20 chars of chunk[0] == first 20 chars of chunk[1]
    assert chunks[0].text[40:60] == chunks[1].text[:20]


def test_chunk_indices_are_sequential():
    text = "X" * 300
    chunks = chunk_text(text, "doc1", "f.txt", "txt", chunk_size=100, chunk_overlap=10)
    for i, chunk in enumerate(chunks):
        assert chunk.chunk_index == i


def test_chunk_metadata_is_preserved():
    chunks = chunk_text("Some text for testing.", "uuid-123", "report.pdf", "pdf", chunk_size=100)
    c = chunks[0]
    assert c.document_id == "uuid-123"
    assert c.filename == "report.pdf"
    assert c.file_type == "pdf"
    assert c.chunk_index == 0
    assert "report.pdf" in c.source
    assert "[chunk 1]" in c.source


def test_source_label_increments_with_index():
    text = "B" * 200
    chunks = chunk_text(text, "d", "f.txt", "txt", chunk_size=80, chunk_overlap=10)
    for i, chunk in enumerate(chunks):
        assert f"[chunk {i + 1}]" in chunk.source


def test_empty_text_returns_no_chunks():
    assert chunk_text("", "doc1", "empty.txt", "txt") == []


def test_whitespace_only_returns_no_chunks():
    assert chunk_text("   \n\t  ", "doc1", "ws.txt", "txt") == []

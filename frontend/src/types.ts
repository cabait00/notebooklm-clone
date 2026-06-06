export interface DocumentResponse {
  document_id: string;
  filename: string;
  file_type: string;
  character_count: number;
  chunk_count: number;
  status: string;
}

export interface Source {
  document_id: string;
  filename: string;
  file_type: string;
  chunk_index: number;
  source: string;
  snippet: string;
  similarity: number;
}

export interface ChatEntry {
  id: string;
  question: string;
  answer: string;
  sources: Source[];
  refused: boolean;
}

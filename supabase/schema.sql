-- QuickPrep Supabase Database Schema
-- Enable the pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create the flashcards table
CREATE TABLE IF NOT EXISTS flashcards (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_text TEXT,
    difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    question_embedding vector(384),  -- Embeddings for question (384 dimensions for all-MiniLM-L6-v2)
    answer_embedding vector(384),    -- Embeddings for answer
    combined_embedding vector(384),  -- Combined question + answer embedding
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS flashcards_user_id_idx ON flashcards(user_id);
CREATE INDEX IF NOT EXISTS flashcards_created_at_idx ON flashcards(created_at DESC);
CREATE INDEX IF NOT EXISTS flashcards_difficulty_idx ON flashcards(difficulty);

-- Create vector similarity search indexes (HNSW for better performance with large datasets)
CREATE INDEX IF NOT EXISTS flashcards_question_embedding_idx ON flashcards 
USING hnsw (question_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS flashcards_answer_embedding_idx ON flashcards 
USING hnsw (answer_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS flashcards_combined_embedding_idx ON flashcards 
USING hnsw (combined_embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Function to search flashcards using vector similarity
CREATE OR REPLACE FUNCTION match_flashcards (
    query_embedding vector(384),
    match_threshold float DEFAULT 0.3,
    match_count int DEFAULT 10,
    user_id_filter text DEFAULT NULL
) 
RETURNS TABLE (
    id bigint,
    question text,
    answer text,
    source_text text,
    difficulty text,
    similarity float,
    created_at timestamptz
) 
LANGUAGE plpgsql 
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        flashcards.id,
        flashcards.question,
        flashcards.answer,
        flashcards.source_text,
        flashcards.difficulty,
        1 - (flashcards.combined_embedding <=> query_embedding) as similarity,
        flashcards.created_at
    FROM flashcards
    WHERE 
        (user_id_filter IS NULL OR flashcards.user_id = user_id_filter)
        AND 1 - (flashcards.combined_embedding <=> query_embedding) > match_threshold
    ORDER BY flashcards.combined_embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_id_param text)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_flashcards', COUNT(*),
        'easy_cards', COUNT(*) FILTER (WHERE difficulty = 'easy'),
        'medium_cards', COUNT(*) FILTER (WHERE difficulty = 'medium'),
        'hard_cards', COUNT(*) FILTER (WHERE difficulty = 'hard'),
        'latest_upload', MAX(created_at),
        'oldest_upload', MIN(created_at)
    )
    INTO result
    FROM flashcards
    WHERE user_id = user_id_param;

    RETURN result;
END;
$$;

-- Function to update flashcard
CREATE OR REPLACE FUNCTION update_flashcard(
    flashcard_id bigint,
    user_id_param text,
    new_question text DEFAULT NULL,
    new_answer text DEFAULT NULL,
    new_difficulty text DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE flashcards 
    SET 
        question = COALESCE(new_question, question),
        answer = COALESCE(new_answer, answer),
        difficulty = COALESCE(new_difficulty, difficulty),
        updated_at = NOW()
    WHERE id = flashcard_id AND user_id = user_id_param;

    RETURN FOUND;
END;
$$;

-- Row Level Security (RLS) policies
ALTER TABLE flashcards ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own flashcards
CREATE POLICY "Users can view own flashcards" ON flashcards
    FOR SELECT USING (auth.uid()::text = user_id);

-- Policy: Users can only insert their own flashcards
CREATE POLICY "Users can insert own flashcards" ON flashcards
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- Policy: Users can only update their own flashcards
CREATE POLICY "Users can update own flashcards" ON flashcards
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Policy: Users can only delete their own flashcards
CREATE POLICY "Users can delete own flashcards" ON flashcards
    FOR DELETE USING (auth.uid()::text = user_id);

-- Create a trigger to automatically update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_flashcards_updated_at 
    BEFORE UPDATE ON flashcards 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

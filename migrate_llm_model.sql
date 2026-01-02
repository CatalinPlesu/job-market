-- Migration script to add llm_model column to job_details table
-- Run this in sqlite3 interactive mode:
--   sqlite3 databases/data.db < migrate_llm_model.sql
-- Or in interactive mode:
--   sqlite3 databases/data.db
--   .read migrate_llm_model.sql

-- Add llm_model column if it doesn't exist
ALTER TABLE job_details ADD COLUMN llm_model VARCHAR(200);

-- Verify the column was added
.schema job_details

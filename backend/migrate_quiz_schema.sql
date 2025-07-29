-- Migration script to update Quiz table from start_date/end_date to date_of_quiz

-- Step 1: Add the new date_of_quiz column
ALTER TABLE quizzes ADD COLUMN date_of_quiz DATETIME;

-- Step 2: Copy start_date values to date_of_quiz for existing records
UPDATE quizzes SET date_of_quiz = start_date WHERE date_of_quiz IS NULL;

-- Step 3: Make date_of_quiz NOT NULL
ALTER TABLE quizzes MODIFY COLUMN date_of_quiz DATETIME NOT NULL;

-- Step 4: Drop the old start_date and end_date columns
ALTER TABLE quizzes DROP COLUMN start_date;
ALTER TABLE quizzes DROP COLUMN end_date; 
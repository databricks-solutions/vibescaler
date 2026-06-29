/**
 * Shared utilities for parsing and formatting rubric questions.
 * This ensures consistent handling of newlines in question descriptions.
 */

import { JudgeType } from '@/client';

// Delimiter used to separate questions in the rubric format
// This special delimiter allows newlines within question descriptions
export const QUESTION_DELIMITER = '|||QUESTION_SEPARATOR|||';

// Delimiter to separate judge type from content within a question
const JUDGE_TYPE_DELIMITER = '|||JUDGE_TYPE|||';

export type QuestionJudgeType = JudgeType;

export interface RubricQuestion {
  id: string;
  title: string;
  description: string;
  judgeType: QuestionJudgeType;
}

/**
 * Parse rubric question text into individual questions.
 * Supports newlines within descriptions by using a special delimiter.
 * Format: "title: description|||JUDGE_TYPE|||judgeType"
 */
export const parseRubricQuestions = (questionText: string): RubricQuestion[] => {
  if (!questionText) return [];
  
  const questionParts = questionText.split(QUESTION_DELIMITER);
  
  return questionParts
    .map((questionText, index): RubricQuestion | null => {
      const trimmedText = questionText.trim();
      if (!trimmedText) return null;
      
      // Check if question has judge type embedded
      let content = trimmedText;
      let judgeType: QuestionJudgeType = JudgeType.LIKERT; // default
      
      if (trimmedText.includes(JUDGE_TYPE_DELIMITER)) {
        const [contentPart, typePart] = trimmedText.split(JUDGE_TYPE_DELIMITER);
        content = contentPart.trim();
        const parsedType = typePart?.trim() as JudgeType;
        if (parsedType === JudgeType.LIKERT || parsedType === JudgeType.BINARY) {
          judgeType = parsedType;
        }
      }
      
      // Split only at the first colon to separate title from description
      const colonIndex = content.indexOf(':');
      let title: string;
      let description: string;

      if (colonIndex === -1) {
        // No colon found - treat entire text as title with empty description
        title = content.trim();
        description = '';
      } else {
        title = content.substring(0, colonIndex).trim();
        description = content.substring(colonIndex + 1).trim();
      }
      
      return {
        id: `q_${index + 1}`,
        title,
        description,
        judgeType
      };
    })
    .filter((q): q is RubricQuestion => q !== null);
};

/**
 * Format rubric questions into a single string.
 * Supports newlines within descriptions by using a special delimiter.
 * Includes judge type for each question.
 */
export const formatRubricQuestions = (questions: RubricQuestion[]): string => {
  if (!questions || questions.length === 0) return '';

  return questions
    .map(q => `${q.title}: ${q.description}${JUDGE_TYPE_DELIMITER}${q.judgeType}`)
    .join(QUESTION_DELIMITER);
};

export interface CriterionDescriptionFields {
  definition: string;
  positive: string;
  negative: string;
  examples: string;
}

const POSITIVE_PREFIX = 'Positive: ';
const NEGATIVE_PREFIX = 'Negative: ';
const EXAMPLES_PREFIX = 'Examples: ';

/**
 * Build a serialized criterion description from structured fields.
 * Multi-line field values are preserved as-is.
 */
export const buildCriterionDescription = (fields: CriterionDescriptionFields): string => {
  const parts: string[] = [];
  if (fields.definition.trim()) parts.push(fields.definition.trim());
  if (fields.positive.trim()) parts.push(`${POSITIVE_PREFIX}${fields.positive.trim()}`);
  if (fields.negative.trim()) parts.push(`${NEGATIVE_PREFIX}${fields.negative.trim()}`);
  if (fields.examples.trim()) parts.push(`${EXAMPLES_PREFIX}${fields.examples.trim()}`);
  return parts.join('\n');
};

/**
 * Parse a serialized criterion description back into structured fields.
 * Section markers (Positive/Negative/Examples) start a section; subsequent
 * lines belong to that section so multi-line values round-trip intact.
 */
export const parseCriterionDescription = (description: string): CriterionDescriptionFields => {
  const sections: Record<keyof CriterionDescriptionFields, string[]> = {
    definition: [],
    positive: [],
    negative: [],
    examples: [],
  };
  let current: keyof CriterionDescriptionFields = 'definition';

  for (const line of (description || '').split('\n')) {
    if (line.startsWith(POSITIVE_PREFIX)) {
      current = 'positive';
      sections[current].push(line.slice(POSITIVE_PREFIX.length));
    } else if (line.startsWith(NEGATIVE_PREFIX)) {
      current = 'negative';
      sections[current].push(line.slice(NEGATIVE_PREFIX.length));
    } else if (line.startsWith(EXAMPLES_PREFIX)) {
      current = 'examples';
      sections[current].push(line.slice(EXAMPLES_PREFIX.length));
    } else {
      sections[current].push(line);
    }
  }

  return {
    definition: sections.definition.join('\n').trim(),
    positive: sections.positive.join('\n').trim(),
    negative: sections.negative.join('\n').trim(),
    examples: sections.examples.join('\n').trim(),
  };
};


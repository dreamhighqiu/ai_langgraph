

/**
 * Prompt Orchestration System
 * 
 * Exports all components of the prompt orchestration system for AI-based test generation.
 * 
 * @module prompts
 */
// TODO  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WVVwS2N3PT06MTkzOGZlZWI=

const generationPrompts = require('./generation-prompts');
const validationRules = require('./validation-rules');
const healingPrompts = require('./healing-prompts');
const PromptOrchestrator = require('./orchestrator');

module.exports = {
  // Main orchestrator class
  PromptOrchestrator,
  
  // Individual components
  generationPrompts,
  validationRules,
  healingPrompts,
  
  // Convenience factory
  createOrchestrator: (options) => new PromptOrchestrator(options)
};
// eslint-disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WVVwS2N3PT06MTkzOGZlZWI=

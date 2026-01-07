/**
 * 版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。
 * 
 * 本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
 * 不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。
 * 
 * 授权商业应用请联系微信：huice666
 */

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

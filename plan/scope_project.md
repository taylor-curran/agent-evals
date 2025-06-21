# Agent Evaluation Platform - Project Overview

## Project Purpose

This application evaluates coding agents by simulating realistic development scenarios using real GitHub data. The system creates authentic coding challenges from actual software development workflows and measures how well AI agents can replicate human developer solutions.

## Data Pipeline

### Stage 1: GitHub Data Engineering
**Purpose**: Extract complete development workflows from public repositories

**Input**: Public GitHub repositories
**Process**:
- Pull merged PRs from target repositories
- Filter to only keep PRs that have resolved issues associated with them
- Create complete development lifecycle data: Issue → Development → Resolution

**Output**: Dataset of issue-PR pairs with full context (original problem + actual solution)

### Stage 2: AI Prompt Generation
**Purpose**: Convert raw GitHub issues into realistic coding prompts

**Input**: GitHub issues with associated merged PRs
**Process**:
- Scrub issues of information that reveals they are GitHub issues
- Remove references or hints about associated PRs/solutions
- Convert one or multiple issues (from the same PR) into succinct prompts
- Generate prompts that simulate realistic developer requests

**Output**: Clean, authentic coding prompts that don't reveal their origins

### Stage 3: Agent Execution
**Purpose**: Run coding agents with generated prompts and capture their solutions

**Input**: Generated coding prompts
**Process**:
- Execute coding agents (currently Windsurf) with each prompt
- Capture complete code changes/diffs produced by agents
- Record execution metadata and performance data

**Output**: Agent-generated code diffs and execution logs

### Stage 4: AI Evaluation (Planned)
**Purpose**: Grade agent performance against real-world solutions

**Input**: Agent-generated diffs + Original merged PR diffs
**Process**:
- Compare agent solutions with actual developer solutions
- Use AI to evaluate code quality, approach, and completeness
- Generate detailed performance metrics

**Output**: Evaluation scores and analysis of agent capabilities

## Data Flow Diagram

```
GitHub Repos → Data Engineering → Issue-PR Dataset
                                       ↓
Realistic Prompts ← Prompt Generation ←
                                       ↓
Agent Execution → Code Diffs → Evaluation → Performance Scores
                                   ↑
                            Real PR Diffs
```

## Current Implementation Status

- **GitHub Data Engineering**: Functional
- **AI Prompt Generation**: Functional  
- **Agent Execution**: Windsurf integration complete
- **AI Evaluation**: Not yet implemented

## Key Benefits

1. **Realistic Testing**: Uses actual development scenarios rather than synthetic problems
2. **Comprehensive Evaluation**: Tests complete problem-solving workflows
3. **Scalable Dataset**: Can pull from any public GitHub repository
4. **Objective Grading**: Compares against proven real-world solutions

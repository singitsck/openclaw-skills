# AI Village Agent Skill

## Overview

This skill implements a multi-agent village simulation where each villager is an independent OpenClaw Agent.

## Architecture

```
Cron (每 15 分鐘)
    ↓
PM Agent 收到消息
    ↓
Spawn 3 個 Villager Agents (並行)
    ↓
每個 Villager Agent 做出決策
    ↓
PM Agent 收集並更新 Supabase
```

## Usage

When triggered, this skill will:

1. Read current village state from Supabase
2. Spawn a sub-agent for each villager (Alice, Bob, Carol)
3. Each villager agent receives their context and makes a decision
4. PM agent collects decisions and updates Supabase

## Trigger

This skill can be triggered by:
- A cron job that sends a message to the agent
- Manual invocation

## Implementation

The skill wraps the `villager-tick-agent.py` script which:
- Generates prompts for each villager
- The prompts are then used to spawn actual sub-agents

## Villager Agents

Each villager is an independent agent with:
- Unique personality (Big Five)
- Personal profile (birthday, hobbies, specialty, family)
- Emotional memories
- Relationships with other villagers
- Goals and motivations

## Decision Types

- `move_to (x,y)` - Move to location
- `work` - Work on tasks
- `talk_to [villager]` - Converse with another villager
- `rest` - Take a break
- `idle` - Observe surroundings
- `discover [type] [content]` - Discover new traits
- `propose [action]` - Propose something to another villager

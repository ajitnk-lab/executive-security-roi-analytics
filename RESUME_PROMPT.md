# Session Resume Prompt

Use this prompt when resuming work after context overflow, CLI crash, session loss, or instance restart:

## 🔄 **Full Resume Prompt**

```
I'm resuming work on the Executive Security ROI Analytics Solution project. 

Project location: /persistent/home/ubuntu/workspace/executive-security-roi-analytics

Please:
1. Load the active TODO list (ID: 1760698452360) 
2. Read the project documentation (README.md, requirements.md, design.md, tasks.md)
3. Check current project status and continue from where we left off
4. Update active-todo-list.md as tasks are completed

Architecture: Executive Dashboard → Bedrock Agent → AgentCore Gateway → 3 MCP Agents (Security/Cost/ROI) on AgentCore Runtime

Key files to review:
- active-todo-list.md (current progress - KEEP THIS UPDATED)
- tasks.md (implementation roadmap) 
- requirements.md (specifications)
- design.md (architecture decisions)

What's the current status and what should we work on next?
```

## 🎯 **Short Resume Prompt**

```
Resume Executive Security ROI Analytics project at /persistent/home/ubuntu/workspace/executive-security-roi-analytics. Load TODO list ID: 1760698452360, update active-todo-list.md, and continue implementation.
```

## 📋 **What This Does**

1. **Loads Active TODO**: Gets the exact task list being tracked (ID: 1760698452360)
2. **Reviews Documentation**: Reads all project specs and architecture decisions
3. **Checks Status**: Sees what's completed vs remaining tasks
4. **Provides Context**: Reminds of the full architecture and approach
5. **Asks for Next Steps**: Gets oriented on what to work on next

## 📁 **Key Files to Check**

- `active-todo-list.md` - Current progress tracking
- `tasks.md` - Detailed implementation roadmap (25 steps)
- `requirements.md` - Complete specifications 
- `design.md` - Architecture and design decisions
- `README.md` - Project overview and quick start
- Project structure and any implemented code

## 🏗️ **Architecture Reminder**

```
Executive Dashboard (React + Embedded Chatbot)
                    ↓
            Bedrock Agent (Orchestrator)
                    ↓
            AgentCore Gateway
        ↓           ↓           ↓
Security MCP    Cost MCP    ROI MCP
(AgentCore)    (AgentCore)  (AgentCore)
```

## 🎯 **Project Status**

- **Current Phase**: Phase 0 (Project Setup and Prerequisites)
- **Completed**: 2/28 tasks (Documentation and structure setup)
- **Next**: Prerequisites check and CDK project initialization
- **Timeline**: 7-11 weeks total estimated

---
*Created: 2025-10-17T11:09:33*
*TODO List ID: 1760698452360*

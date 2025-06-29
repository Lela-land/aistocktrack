# aistocktrack

## Quick Start

1. **Read CLAUDE.md first** - Contains essential rules for Claude Code
2. Follow the pre-task compliance checklist before starting any work
3. Use proper module structure under `src/main/python/`
4. Commit after every completed task

## Project Overview

**aistocktrack** is a merchandise inventory monitoring website that generates different frontend HTML interfaces based on a unified data stream. The system focuses on:

- **Unified Backend**: Single data source providing product information
- **Brand-Specific Frontends**: Pop Mart and Pokémon card themed interfaces
- **Data Stream**: Product name, source, purchase link, price, stock levels, images/videos
- **Frontend Focus**: Matching brand identity while maintaining backend consistency

## Project Structure

**Standard Projects:** Full application structure with modular organization  

```
src/main/python/
├── core/      # Core business logic
├── utils/     # Utility functions/classes
├── models/    # Data models/entities
├── services/  # Service layer
└── api/       # API endpoints/interfaces
```

## Development Guidelines

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating  
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - works with Python, JS, Java, etc.
- **Scalable** - start simple, grow as needed
- **Flexible** - choose complexity level based on project needs
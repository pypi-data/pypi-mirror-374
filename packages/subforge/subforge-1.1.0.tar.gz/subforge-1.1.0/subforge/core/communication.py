#!/usr/bin/env python3
"""
Communication Manager - SubForge Factory
Manages inter-agent communication via structured markdown files
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class CommunicationManager:
    """Manages structured communication between factory agents"""

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.communication_dir = workspace_dir / "communication"
        self.handoffs_dir = self.communication_dir / "handoffs"

        # Create communication directories
        for directory in [self.communication_dir, self.handoffs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    async def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        handoff_type: str,
        data: Dict[str, Any],
        instructions: str,
    ) -> str:
        """Create a formal handoff between agents"""

        handoff_id = f"handoff_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(from_agent + to_agent) % 1000:03x}"

        handoff_data = {
            "handoff_id": handoff_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "handoff_type": handoff_type,
            "data": data,
            "instructions": instructions,
            "timestamp": datetime.now().isoformat(),
            "status": "created",
        }

        # Save as JSON
        handoff_file = self.handoffs_dir / f"{handoff_id}.json"
        with open(handoff_file, "w") as f:
            json.dump(handoff_data, f, indent=2)

        # Save as Markdown for readability
        handoff_md = f"""# Handoff: {handoff_id}

**From**: @{from_agent}  
**To**: @{to_agent}  
**Type**: {handoff_type}  
**Created**: {handoff_data['timestamp']}

## Instructions
{instructions}

## Data
```json
{json.dumps(data, indent=2)}
```
"""

        handoff_md_file = self.handoffs_dir / f"{handoff_id}.md"
        with open(handoff_md_file, "w") as f:
            f.write(handoff_md)

        print(f"    📨 Created handoff {handoff_id}: @{from_agent} → @{to_agent}")
        return handoff_id
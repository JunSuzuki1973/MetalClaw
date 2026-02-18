---
name: agent-zero
description: "Interact with Agent Zero via Docker commands."
metadata: {"nanobot":{"emoji":"🤖","requires":{"bins":["docker"]}}}
---

# Agent Zero Skill

Interact with Agent Zero running in the Docker container.

## Run Agent Zero

Execute a command in Agent Zero:
```bash
docker exec agent-zero bash -c "cd /root/.openclaw/workspace/agent-zero && source venv/bin/activate && python agent.py --message '{{message}}'"
```

## View Status

Check Agent Zero status:
```bash
docker exec agent-zero bash -c "docker ps --filter name=agent-zero --format '{{.Status}}'"
```

## Restart Agent Zero

Restart the Agent Zero container:
```bash
docker exec agent-zero bash -c "docker restart agent-zero"
```

## View Logs

View Agent Zero logs:
```bash
docker exec agent-zero bash -c "docker logs agent-zero --tail 50"
```

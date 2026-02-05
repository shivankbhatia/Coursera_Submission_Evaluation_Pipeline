from agents.tool_registry import TOOL_REGISTRY

print("Available Tools:\n")

for tool_name, tool in TOOL_REGISTRY.items():
    print(tool_name, "→", tool.description)

# test_agentos_routes.py - Explorar rotas do AgentOS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.os import AgentOS
from agno.tools.duckduckgo import DuckDuckGoTools

# Create a simple agent
agent = Agent(
    name="TestAgent",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    instructions="You are a helpful assistant."
)

# Setup AgentOS
agent_os = AgentOS(
    description="Test AgentOS",
    agents=[agent],
)

# Get the app
app = agent_os.get_app()

# Get all routes
routes = agent_os.get_routes()

print("=== AGENTOS ROUTES ===")
for route in routes:
    print(f"Route: {route.path}")
    if hasattr(route, 'methods'):
        print(f"Methods: {route.methods}")
    print(f"Name: {route.name}")
    print("---")

print(f"\nTotal routes: {len(routes)}")

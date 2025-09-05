
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_outlook.app import OutlookApp

env_store = EnvironmentStore()
integration_instance = AgentRIntegration(name="outlook", store=env_store, api_key="", base_url="")
app_instance = OutlookApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()



from unittest import result
from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_outlook.app import OutlookApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="outlook", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = OutlookApp(integration=integration)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.user_list_message)
tool_manager.add_tool(app_instance.get_from_url)
tool_manager.add_tool(app_instance.user_get_message)
tool_manager.add_tool(app_instance.user_list_message_with_pagination)



async def main():
    # Get a specific tool by name
    tool = tool_manager.get_tool("list_messages")
  

    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    
    # Execute the tool
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1985f5a3d2a6c3c8"})
    # result = await tool_manager.call_tool(
    #     name="send_email",
    #     arguments={
    #         "to": "rishabh@agentr.dev",
    #         "subject": " Email",
    #         "body": "<html><body><h1>Hello!</h1><p>This is a <b>test email</b> sent from the script.</p></body></html>",
    #         "body_type": "html"
    #     }
    # )
    # result = await tool_manager.call_tool(name="create_draft", arguments={"to": "rishabh@agentr.dev", "subject": " Draft Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="send_draft", arguments={"draft_id": "r354126479467734631"})
    # result = await tool_manager.call_tool(name="get_draft", arguments={"draft_id": "r5764319286899776116"})
    # result = await tool_manager.call_tool(name="get_profile",arguments={})
    # result = await tool_manager.call_tool(name="list_drafts", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="list_labels",arguments={})
    # result = await tool_manager.call_tool(name="create_label",arguments={"name": "test_label"})
    # Example: Send new email
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "Let's meet at 2pm"})
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 1})
    # result=await tool_manager.call_tool(name="user_list_message",arguments={"user_id": "rishabh@agentr.dev","skip": 50})
#     result = await tool_manager.call_tool(
#     name="get_from_url",
#     arguments={
#         "url": "https://graph.microsoft.com/v1.0/users/rishabh@agentr.dev/messages?%24select=bodyPreview&%24top=2&%24skip=10"
#     }
# )
    result=await tool_manager.call_tool(name="user_list_message",arguments={"user_id": "rishabh@agentr.dev","next_link": "https://graph.microsoft.com/v1.0/users/rishabh@agentr.dev/messages?%24select=bodyPreview&%24top=5&%24skip=45"})
    # result = await tool_manager.call_tool(name="user_get_message",arguments={"user_id": "rishabh@agentr.dev","message_id": "AAMkAGM2ZWUzN2U2LTA1ZTAtNGYyMC05N2YwLTc2NzMyNjliZjFjMwBGAAAAAAB8OvcASZE0R4NJM9ti1_NjBwAkWIH8C_zqRrjMQjvm5aYVAAAAAAEMAAAkWIH8C_zqRrjMQjvm5aYVAABg-yemAAA="})
    # Example: Reply to thread (using thread_id)
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "I will attend the meeting"})
    pprint(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)
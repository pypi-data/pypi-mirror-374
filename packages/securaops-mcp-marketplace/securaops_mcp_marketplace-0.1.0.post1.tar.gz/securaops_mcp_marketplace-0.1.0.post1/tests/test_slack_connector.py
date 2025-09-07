from securaops_mcp_marketplace import SlackConnector

# Initialize with your API key
connector = SlackConnector("your_slack_api_key")

# Send a message
result = connector.send_message(
    channel="#general", 
    message="Hello from my LLM!"
)

print(result)  # {"status": "sent", "message_id": "1234567890"}
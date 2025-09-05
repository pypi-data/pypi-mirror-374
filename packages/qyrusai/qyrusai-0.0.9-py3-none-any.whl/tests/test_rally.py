import asyncio
from qyrusai._clients import AsyncQyrusAI,SyncQyrusAI
import traceback


# Test Structure (NOVA)
async def main_test():
    at = "33fe8e15-e903-4dd5-9120-52d98c1e674c"
    # client = AsyncQyrusAI(api_key=at)
    client=SyncQyrusAI(api_key=at)
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "hemanths@quinnox.com"
    jira_api_token = None
    jira_ticket_id = "1234"
    TICKET_ID="US1"
    WORKSPACE_NAME="RALLY DEMO DATA"
    RALLY_URL="https://rally1.rallydev.com"
    RALLY_API_KEY="Bearer _2xDz9kIvRQy9c2pXYuon5kqVWhihREGklXGOJw9hy"
    try:
        # op = await client.nova.from_rally.create(TICKET_ID=TICKET_ID,
        #                                     WORKSPACE_NAME=WORKSPACE_NAME,
        #                                     RALLY_URL=RALLY_URL,
        #                                     RALLY_API_KEY=RALLY_API_KEY,
        #                                     )
        op=client.nova.from_rally.create(TICKET_ID=TICKET_ID,
                                            WORKSPACE_NAME=WORKSPACE_NAME,
                                            RALLY_URL=RALLY_URL,
                                            RALLY_API_KEY=RALLY_API_KEY,
                                        )
        return op
    except Exception as e:
        print(e.message)
        print(traceback.format_exc())


if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main_test()))

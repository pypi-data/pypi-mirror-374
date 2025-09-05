import asyncio
from qyrusai._clients import AsyncQyrusAI
import traceback


# Test Structure (NOVA)
async def main_test():
    at = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=at)
    # "invalid_jira_id_input":
#     [["123--ui", "https://cogcloud.atlassian.net", "valid_api_token", "h@quinnox.com"],--- REQUESTEXCEPTION
#      [None, "https://cogcloud.atlassian.net", "valid_api_token", "h@quinnox.com"],
#      [123, "https://cogcloud.atlassian.net", "valid_api_token", "h@quinnox.com"]],
    
#     "invalid_jira_endpoint_input":
#     [["correct_jira_id", "[]", "valid_api_token", "h@quinnox.com"],------Bad Request
#      ["correct_jira_id", None, "valid_api_token", "h@quinnox.com"],
#      ["correct_jira_id", 789, "valid_api_token", "h@quinnox.com"]],
    
#     "invalid_jira_username_input":
#     [["correct_jira_id", "https://cogcloud.atlassian.net", "valid_api_token", "{}" "$$$**"],----request exception
#      ["correct_jira_id", "https://cogcloud.atlassian.net", "valid_api_token", "[]"],
#      ["correct_jira_id", "https://cogcloud.atlassian.net", "valid_api_token", None]],
# invalid_api_token:None= Bad request
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "hemanths@quinnox.com"
    jira_api_token = None
    jira_ticket_id = "1234"
    try:
        op = await client.nova.from_jira.create(jira_api_token=jira_api_token,
                                            jira_endpoint=jira_endpoint,
                                            jira_username=jira_username,
                                            jira_id=jira_ticket_id)
    # @pytest.mark.parametrize("image_url", ["**", "67.09", "None", "", "[]no", "{}"])
        # # response_body=None
        # response_body="**&&&"
        # output = await client.api_assertions.jsonbody.create(response_body)
        return op
    except Exception as e:
        print(e.message)
        print(traceback.format_exc())


if __name__ == "__main__":
    import asyncio
    print(asyncio.run(main_test()))

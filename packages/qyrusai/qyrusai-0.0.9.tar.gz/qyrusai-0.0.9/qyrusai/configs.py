import httpx


class Configurations:

    def verifyToken(ai_token: str):
        url = f"https://stg-gateway.qyrus.com:8243/authentication/v1/api/validateAPIToken?apiToken={ai_token}"
        with httpx.Client(timeout=600) as client:
            response = client.get(
                url=url,
                headers={
                    "Authorization":
                    "Bearer 90540897-748a-3ef2-b3a3-c6f8f42022da"
                })
            response.raise_for_status()
            data = response.json()
            # print("\nDATA for verify token : ", data)
            if data.get("message"
                        ) == "Authentication Token Validated Successfully.":
                return True  # ai token is correct
            else:
                raise Exception("401")  # mostly tells ai token is wrong

    def getDefaultGateway(ai_token: str):
        url = f"https://stg-gateway.qyrus.com:8243/authentication/v1/api/authenticateAPIToken?apiToken={ai_token}"
        with httpx.Client(timeout=600) as client:
            response = client.get(
                url,
                headers={
                    "Authorization":
                    "Bearer 90540897-748a-3ef2-b3a3-c6f8f42022da"
                })
            response.raise_for_status()
            data = response.json()
            # print("\nDATA for gateway details :", data)
            if data.get("status", False):
                del data["uuid"]
                return data
            else:
                raise Exception("401")

    def getNovaContextPath(_from: str):
        return f"nova-sdk/v1/api/nova_{_from}"

    def getApiBuilderContextPath(_from: str):
        return f"api-builder-sdk/v1/api/{_from}"

    def getDataAmplifierContextPath():
        return f"synthetic-data-generator-sdk/v1/api/datagen"

    def getAPIAssertions(_from: str):
        return f"api-assertion-gpt-sdk/v1/api/assertion/{_from}"

    def getVisionNovaContextPath(_from: str):
        return f"vision-nova-sdk/v1/api/{_from}"

    def getLLMEvaluatorContextPath(_from: str):
        return f"llm-evaluator-sdk/v1/{_from}"

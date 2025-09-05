import pytest
from qyrusai._clients import AsyncQyrusAI, SyncQyrusAI
from qyrusai.nova.nova import CreateScenariosResponse
import httpx
from qyrusai._exceptions import RequestException, EntityException
from qyrusai.data_amplifier.data_amplifier import DataAmplifierResponse
"""--------------------------------------------------------NOVA-------------------------------------------------------"""


@pytest.mark.asyncio
async def test_create_scenarios_from_description():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    operation = await client.nova.from_description.create(
        "Create tests for login page")
    assert isinstance(operation, CreateScenariosResponse)
    # print(operation)
    assert operation.ok == True
    assert operation.message == "generated successfully"
    assert isinstance(operation.scenarios, list)
    for scenario in operation.scenarios:
        assert hasattr(scenario, 'criticality_score')
        assert hasattr(scenario, 'criticality_description')
        assert hasattr(scenario, 'reason_to_test')
        assert hasattr(scenario, 'test_script_objective')
        assert hasattr(scenario, 'test_script_name')

        assert isinstance(scenario.criticality_score, int)
        assert isinstance(scenario.criticality_description, str)
        assert isinstance(scenario.reason_to_test, str)
        assert isinstance(scenario.test_script_objective, str)
        assert isinstance(scenario.test_script_name, str)


@pytest.mark.asyncio
async def test_invalid_token_jira_Description():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = AsyncQyrusAI(api_key=api_token)
        await client.from_description.create("Create tests for login page")

    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)
    assert exc_info.value.request.url == "https://stg-gateway.qyrus.com:8243/authentication/v1/api/validateAPIToken?apiToken="


@pytest.mark.parametrize("desc", ["67.09", "", "[]", "{}"])
@pytest.mark.asyncio
async def test_invalid_input_from_Description(desc):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(RequestException) as exc_info:
        await client.nova.from_description.create(desc)
    # Assert that the exception contains the expected error message
    assert "Internal Server Error" in str(exc_info.value)
    assert "unexpected condition" in str(exc_info.value)


def test_create_scenarios_from_jira():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "harshithan@quinnox.com"
    jira_api_token = "ATATT3xFfGF0CtKFWH8_OYg0FqGO-I_ZElph0kM0IL2JkuSCZSVoXZaJXNdkM_ahy5L-F6U4ouerHVNTn0Msd2_dJNzBEGWTIMugzFi0KrQuGS8quGc25p7sdhZm0eIq7vxpMckC2JJtR3opFGy6uQRIFmZkadCdfi3OfHJElO4e7QiNjZN9Xbw=4067488F"
    jira_ticket_id = "MON-5"
    operation = client.nova.from_jira.create(jira_api_token=jira_api_token,jira_endpoint=jira_endpoint,jira_username=jira_username,jira_id=jira_ticket_id)
    # print(f"this is operation {operation}")
    assert isinstance(operation, CreateScenariosResponse)
    # print(operation)
    assert operation.ok == True
    assert operation.message == "generated successfully"
    assert isinstance(operation.scenarios, list)
    for scenario in operation.scenarios:
        assert hasattr(scenario, 'criticality_score')
        assert hasattr(scenario, 'criticality_description')
        assert hasattr(scenario, 'reason_to_test')
        assert hasattr(scenario, 'test_script_objective')
        assert hasattr(scenario, 'test_script_name')

        assert isinstance(scenario.criticality_score, int)
        assert isinstance(scenario.criticality_description, str)
        assert isinstance(scenario.reason_to_test, str)
        assert isinstance(scenario.test_script_objective, str)
        assert isinstance(scenario.test_script_name, str)


@pytest.mark.parametrize("jira_id", ["67.09", "", "123--ui", "{}"])
@pytest.mark.asyncio
async def test_invalid_jira_id(jira_id):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "hemanths@quinnox.com"
    jira_api_token = "ATATT3xFfGF0fUUfKLRzDyOhew0MVyCzJVnR7v91x5wnVV2VB3vfbahpvFONkQM0gTEb2sCFdTJ9fXRiN903qqZH0VQrNsokc1HixcY72Z9D_60r4Fsm2zy70hw9-fAfTnB-8WqkacGe2LBJx0CrEFXeTLLaEfdPU6EEIrEnshZj_985yPnBftc=7711CE3F"
    jira_ticket_id = jira_id
    with pytest.raises(RequestException) as exc_info:
        await client.nova.from_jira.create(jira_endpoint, jira_api_token,
                                           jira_username, jira_ticket_id)
    assert "Internal Server Error" in str(exc_info.value)
    assert "unexpected condition" in str(exc_info.value)


def test_invalid_jira_endpoint():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    jira_endpoint = 123
    jira_username = "hemanths@quinnox.com"
    jira_api_token = "ATATT3xFfGF0fUUfKLRzDyOhew0MVyCzJVnR7v91x5wnVV2VB3vfbahpvFONkQM0gTEb2sCFdTJ9fXRiN903qqZH0VQrNsokc1HixcY72Z9D_60r4Fsm2zy70hw9-fAfTnB-8WqkacGe2LBJx0CrEFXeTLLaEfdPU6EEIrEnshZj_985yPnBftc=7711CE3F"
    jira_ticket_id = "MON-5"
    with pytest.raises(EntityException) as exc_info:
        client.nova.from_jira.create(jira_endpoint, jira_api_token,
                                     jira_username, jira_ticket_id)
    assert "Bad Request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_jira_username():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "$&^^*"
    jira_api_token = "ATATT3xFfGF0fUUfKLRzDyOhew0MVyCzJVnR7v91x5wnVV2VB3vfbahpvFONkQM0gTEb2sCFdTJ9fXRiN903qqZH0VQrNsokc1HixcY72Z9D_60r4Fsm2zy70hw9-fAfTnB-8WqkacGe2LBJx0CrEFXeTLLaEfdPU6EEIrEnshZj_985yPnBftc=7711CE3F"
    jira_ticket_id = "MON-5"
    with pytest.raises(RequestException) as exc_info:
        await client.nova.from_jira.create(jira_endpoint, jira_api_token,
                                           jira_username, jira_ticket_id)
    assert "Internal Server Error" in str(exc_info.value)
    assert "unexpected condition" in str(exc_info.value)


def test_invalid_jira_token():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    jira_endpoint = "https://cogcloud.atlassian.net"
    jira_username = "hemanths@quinnox.com"
    jira_api_token = None
    jira_ticket_id = "MON-5"
    with pytest.raises(EntityException) as exc_info:
        client.nova.from_jira.create(jira_endpoint, jira_api_token,
                                     jira_username, jira_ticket_id)
    assert "Bad Request" in str(exc_info.value)


"""-------------------------------------------------------VISION NOVA---------------------------------------------------"""


@pytest.mark.asyncio
async def test_create_scenarios_from_image():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    image_url = "https://cdn.dribbble.com/userupload/12323124/file/original-00fd2fb0c444a812c1cca08bb78cc49f.jpg"
    output = await client.vision_nova.generate_test.generate(image_url)
    assert 'ok' in output
    assert output['ok']

    for scenario in output['scenarios']:
        assert 'scenario_name' in scenario
        assert 'description' in scenario
        assert 'objective' in scenario
        assert 'steps' in scenario

        assert isinstance(scenario['scenario_name'], str)
        assert isinstance(scenario['description'], str)
        assert isinstance(scenario['objective'], str)
        assert isinstance(scenario['steps'], list)

        for step in scenario['steps']:
            assert isinstance(step, str)

        assert scenario['scenario_name'] != ""
        assert scenario['description'] != ""
        assert scenario['objective'] != ""
        assert len(scenario['steps']) > 0


def test_verify_from_image():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    image_url = "https://cdn.dribbble.com/userupload/12323124/file/original-00fd2fb0c444a812c1cca08bb78cc49f.jpg"
    output = client.vision_nova.verify_accessibility.verify(image_url)
    # print(output)
    assert 'ok' in output
    assert output['ok']
    for verify in output['visual_accessibility']:
        assert 'accessibility_type' in verify
        assert 'accessibility_comment' in verify

        assert isinstance(verify['accessibility_type'], str)
        assert isinstance(verify['accessibility_comment'], str)


def test_invalid_input_from_generate():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    image_url = " 39.00 "
    with pytest.raises(RequestException) as exc_info:
        client.vision_nova.generate_test.generate(image_url)

    # Assert that the exception contains the expected error message
    assert "Internal Server Error" in str(exc_info.value)
    assert "unexpected condition" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_api_token_verify():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = AsyncQyrusAI(api_key=api_token)
        image_url = "https://cdn.dribbble.com/userupload/12323124/file/original-00fd2fb0c444a812c1cca08bb78cc49f.jpg"
        client.vision_nova.verify_accessibility.verify(image_url)

    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("image_url", ["**", "67.09", "None", "", "[]", "{}"])
@pytest.mark.asyncio
async def test_invalid_input_from_verify(image_url):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(RequestException) as exc_info:
        await client.vision_nova.verify_accessibility.verify(image_url)

    # Assert that the exception contains the expected error message
    assert "Internal Server Error" in str(exc_info.value)
    assert "unexpected condition" in str(exc_info.value)


"""-----------------------------------------------------API BUILDER----------------------------------------------------"""


@pytest.mark.asyncio
async def test_apis_from_builder():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    api_design_description = "Create a Home Loan application microservice with 1 API to apply for loan"
    output = await client.api_builder.build(
        email="", user_description=api_design_description)
    # print(output)
    assert isinstance(output, dict)
    assert 'info' in output
    assert isinstance(output['info'], dict)


def test_invalid_api_token_build():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        api_design_description = "Create a Home Loan application microservice with 1 API to apply for loan"
        output = client.api_builder.build(
            email="", user_description=api_design_description)

    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("description", [67.09, None])
@pytest.mark.asyncio
async def test_invalid_input_from_build(description):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        await client.api_builder.build(email="", user_description=description)

    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)


""" --------------------------------------Data Amplifier------------------------------------------------------------"""


@pytest.mark.asyncio
async def test_data_amplifiers():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    data_count = 1
    data = [{
        "column_name": "name",
        "column_description": "name",
        "column_restriction": "no restrictions",
        "column_values": ["Sameer Seikh", "Sunil Dutt"]
    }]
    output = await client.data_amplifier.amplify(data, data_count)
    # print(output)
    assert isinstance(output, DataAmplifierResponse)
    assert output.status == True
    # Optionally, you can add more assertions to verify the structure and content of result.data
    assert 'name' in output.data
    assert isinstance(output.data, dict)
    assert isinstance(output.data['name'], list)


def test_invalid_api_token_amplify():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        data_count = 1
        data = [{
            "column_name": "name",
            "column_description": "name",
            "column_restriction": "no restrictions",
            "column_values": ["Sameer Seikh", "Sunil Dutt"]
        }]
        output = client.data_amplifier.amplify(data, data_count)

    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("data", ["**", "67.09", None, "", {}])
@pytest.mark.asyncio
async def test_invalid_input_from_amplify(data):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        data_count = 1
        await client.data_amplifier.amplify(data, data_count)
    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)


"""-------------------------------API ASSERTIONS------------------------------------------------------------"""
"---------------Headers Test--------------"


@pytest.mark.asyncio
async def test_api_assert_headers():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    headers = {
        "Access-Control-Allow-Credentials: true Access-Control-Allow-Origin: * Content-Length: 166 Content-Type: application/json Date: Wed, 12 Jun 2024 10:29:06 GMT Server: awselb/2.0"
    }
    output = await client.api_assertions.headers.create(f'{headers}')
    print(output)
    assert isinstance(output, list), "Output should be a list"

    for item in output:
        # Ensure each item in the list is a dictionary
        assert isinstance(
            item, dict), "Each item in the output list should be a dictionary"
        # Ensure each dictionary contains the required keys
        assert 'assertHeaderKey' in item, "Each item should contain 'assertHeaderKey'"
        assert 'assertHeaderValue' in item, "Each item should contain 'assertHeaderValue'"
        assert 'assertionDescription' in item, "Each item should contain 'assertionDescription'"

        # Optionally, ensure the types of the values are correct
        assert isinstance(item['assertHeaderKey'], str)
        assert isinstance(item['assertHeaderValue'], str)
        assert isinstance(item['assertionDescription'], str)


def test_invalid_api_token_header():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        headers = {
            "Access-Control-Allow-Credentials: true Access-Control-Allow-Origin: * Content-Length: 166 Content-Type: application/json Date: Wed, 12 Jun 2024 10:29:06 GMT Server: awselb/2.0"
        }
        output = client.api_assertions.headers.create(f'{headers}')

    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("headers", [67.00, None])
@pytest.mark.asyncio
async def test_invalid_input_from_amplify(headers):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        await client.api_assertions.headers.create(headers)
    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)


# """-----------Body Tests-------------"""


def test_api_assert_body():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = SyncQyrusAI(api_key=api_token)
    response_body = [{
        'loanId': 101,
        'amount': 15000.0,
        'interestRate': 4.5,
        'duration': 36,
        'status': 'Active'
    }, {
        'loanId': 102,
        'amount': 8000.0,
        'interestRate': 3.0,
        'duration': 12,
        'status': 'Active'
    }]
    output = client.api_assertions.jsonbody.create(response_body)
    print(output)
    for body in output:
        assert 'value' in body
        assert 'type' in body
        assert 'assertionDescription' in body
        assert isinstance(body['value'], str)
        assert isinstance(body['type'], str)
        assert isinstance(body['assertionDescription'], str)


def test_invalid_api_token_body():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        response_body = [{
            'loanId': 101,
            'amount': 15000.0,
            'interestRate': 4.5,
            'duration': 36,
            'status': 'Active'
        }, {
            'loanId': 102,
            'amount': 8000.0,
            'interestRate': 3.0,
            'duration': 12,
            'status': 'Active'
        }]
        output = client.api_assertions.jsonbody.create(response_body)
    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("body", [00.80, None])
@pytest.mark.asyncio
async def test_invalid_input_from_body(body):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        await client.api_assertions.jsonbody.create(body)
    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)


# """----------JSON PATH------------"""


@pytest.mark.asyncio
async def test_api_assert_path():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    response_body = [{
        'loanId': 101,
        'amount': 15000.0,
        'interestRate': 4.5,
        'duration': 36,
        'status': 'Active'
    }]
    output = await client.api_assertions.jsonpath.create(response_body)
    print(output)
    for path in output:
        assert 'jsonPath' in path
        assert 'jsonPathValue' in path
        assert 'type' in path
        assert 'assertionDescription' in path
        assert isinstance(path['jsonPath'], str)
        assert isinstance(path['jsonPathValue'], str)
        assert isinstance(path['type'], str)
        assert isinstance(path['assertionDescription'], str)


def test_invalid_api_token_path():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        response_body = [{
            'loanId': 101,
            'amount': 15000.0,
            'interestRate': 4.5,
            'duration': 36,
            'status': 'Active'
        }]
        output = client.api_assertions.jsonpath.create(response_body)
    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("response_body", [00.80, None])
@pytest.mark.asyncio
async def test_invalid_input_from_path(response_body):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        await client.api_assertions.jsonpath.create(response_body)
    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)


"""---------------SCHEMA TESTS--------------------------"""


@pytest.mark.asyncio
async def test_api_assert_schema():
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    response_body = [{
        'loanId': 101,
        'amount': 15000.0,
        'interestRate': 4.5,
        'duration': 36,
        'status': 'Active'
    }]
    schema = await client.api_assertions.jsonschema.create(response_body)
    assert '$schema' in schema, "Schema must have a $schema key"
    assert 'anyOf' in schema, "Schema must have an anyOf key"
    assert 'title' in schema, "Schema must have a title key"
    assert 'description' in schema, "Schema must have a description key"

    assert isinstance(schema['anyOf'], list), "Schema anyOf must be a list"
    assert all(isinstance(subschema, dict) for subschema in
               schema['anyOf']), "Each item in anyOf must be a dictionary"

    # Verify the $schema, title, and description
    assert schema[
        '$schema'] == "http://json-schema.org/schema#", "Unexpected $schema value"
    assert isinstance(schema['title'], str), "title should be a string"
    assert isinstance(schema['description'],
                      str), "description should be a string"


def test_invalid_api_token_schema():
    api_token = ""
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        client = SyncQyrusAI(api_key=api_token)
        response_body = [{
            'loanId': 101,
            'amount': 15000.0,
            'interestRate': 4.5,
            'duration': 36,
            'status': 'Active'
        }]
        output = client.api_assertions.jsonschema.create(response_body)
    # Verify that the exception contains the expected HTTP status code
    assert exc_info.value.response.status_code == 400
    assert 'Client error' in str(exc_info.value)


@pytest.mark.parametrize("response_body", [00.80, None])
@pytest.mark.asyncio
async def test_invalid_input_from_schema(response_body):
    api_token = "1acf91cc-7c9b-4f99-9ce1-0fa3d0fb854d"
    client = AsyncQyrusAI(api_key=api_token)
    with pytest.raises(EntityException) as exc_info:
        await client.api_assertions.jsonschema.create(response_body)
    # Assert that the exception contains the expected error message
    assert "Bad Request" in str(exc_info.value)

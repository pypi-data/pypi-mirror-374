# Machine

Types:

```python
from elicit.types import MachineLearnResponse, MachineQueryResponse
```

Methods:

- <code title="post /v1/machine/learn">client.machine.<a href="./src/elicit/resources/machine.py">learn</a>(\*\*<a href="src/elicit/types/machine_learn_params.py">params</a>) -> <a href="./src/elicit/types/machine_learn_response.py">MachineLearnResponse</a></code>
- <code title="post /v1/machine/query">client.machine.<a href="./src/elicit/resources/machine.py">query</a>(\*\*<a href="src/elicit/types/machine_query_params.py">params</a>) -> <a href="./src/elicit/types/machine_query_response.py">MachineQueryResponse</a></code>

# Users

Types:

```python
from elicit.types import UserCreateOrGetResponse
```

Methods:

- <code title="post /v1/users">client.users.<a href="./src/elicit/resources/users.py">create_or_get</a>(\*\*<a href="src/elicit/types/user_create_or_get_params.py">params</a>) -> <a href="./src/elicit/types/user_create_or_get_response.py">UserCreateOrGetResponse</a></code>

# Data

Types:

```python
from elicit.types import DataIngestResponse
```

Methods:

- <code title="post /v1/data/ingest">client.data.<a href="./src/elicit/resources/data/data.py">ingest</a>(\*\*<a href="src/elicit/types/data_ingest_params.py">params</a>) -> <a href="./src/elicit/types/data_ingest_response.py">DataIngestResponse</a></code>

## Job

Types:

```python
from elicit.types.data import JobRetrieveStatusResponse
```

Methods:

- <code title="post /v1/data/job/status">client.data.job.<a href="./src/elicit/resources/data/job.py">retrieve_status</a>(\*\*<a href="src/elicit/types/data/job_retrieve_status_params.py">params</a>) -> <a href="./src/elicit/types/data/job_retrieve_status_response.py">JobRetrieveStatusResponse</a></code>

# APIKeys

Types:

```python
from elicit.types import APIKeyCreateResponse, APIKeyListResponse, APIKeyRevokeResponse
```

Methods:

- <code title="post /v1/api-keys/">client.api_keys.<a href="./src/elicit/resources/api_keys.py">create</a>(\*\*<a href="src/elicit/types/api_key_create_params.py">params</a>) -> <a href="./src/elicit/types/api_key_create_response.py">APIKeyCreateResponse</a></code>
- <code title="get /v1/api-keys/">client.api_keys.<a href="./src/elicit/resources/api_keys.py">list</a>() -> <a href="./src/elicit/types/api_key_list_response.py">APIKeyListResponse</a></code>
- <code title="delete /v1/api-keys/{api_key_id}">client.api_keys.<a href="./src/elicit/resources/api_keys.py">revoke</a>(api_key_id) -> <a href="./src/elicit/types/api_key_revoke_response.py">APIKeyRevokeResponse</a></code>

# Health

Methods:

- <code title="get /health">client.health.<a href="./src/elicit/resources/health.py">check</a>() -> object</code>

# Vizlook

The official Vizlook Python SDK.

## Install

```bash
pip install vizlook
```

## Usage

```python
from vizlook import Vizlook, AsyncVizlook

vizlook = Vizlook(api_key=os.environ.get("VIZLOOK_API_KEY"))
```

Performs a video search on the Vizlook system.

```python
response = vizlook.search(
    "how to be productive",
    max_results=5,
    start_published_date="2025-08-19T15:01:36.000Z",
    need_transcription=True,
    need_summary=True,
)

print("response with original API key:", response.to_dict())
print("response with snake case key:", response.to_dict(use_api_field_name=False))
```

Generates an answer to a query.

```python
response = vizlook.answer("how to be productive", need_transcription=True)
```

Streams an answer to a query.

```python
stream = vizlook.stream_answer("how to be productive")
answer = ""

for chunk in stream:
    # response with original API key
    chunk_dict = chunk.to_dict()
    chunk_type = chunk_dict.get("type")

    if chunk_type == "answer-chunk":
        answer += chunk_dict.get("data", "")
    if chunk_type == "data-citations":
        print("Citations: ", chunk_dict.get("data").get("citations"))
    if chunk_type == "data-cost":
        print("Cost: ", chunk_dict.get("data").get("dollarCost"))
    if chunk_type == "error":
        print("Error: ", chunk_dict.get("data").get("errorText"))

print("Answer: ", answer)
```

Retrieves contents of videos based on specified URLs.

```python
response = vizlook.get_video_contents(
  "https://www.youtube.com/watch?v=QdBokRd2ahw",
  crawl_mode="Always",
)
```

## Documentation

https://docs.vizlook.com

## API

https://docs.vizlook.com/documentation/api-reference/search

## Contributing

Feel free to submit pull requests. For larger-scale changes, though, it's best to open an issue first so we can deliberate on your plans.

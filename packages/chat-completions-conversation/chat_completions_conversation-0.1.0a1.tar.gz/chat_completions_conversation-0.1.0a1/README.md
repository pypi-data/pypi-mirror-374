A Python 2+ library for conversations with LLMs providing
an [OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat)-compatible API. That includes OpenAI's
models, Google Gemini, DeepSeek, and anything you can run on ollama.

## Features

- **Compatibility:** Unlike [openai](https://github.com/openai/openai-python), works on Python 2+ with zero non-Python
  dependencies.
- **Streaming Responses:** Obtain responses as they're generated.
- **Conversation Persistence:** Save/load conversations in JSON format.

## Installation

```bash
pip install chat-completions-conversation
```

## Usage

Suppose we interface with a VLM, and have the following `messages.json` file under the current working directory:

```json
[
    
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/640px-PNG_transparency_demonstration_1.png"
                }
            },
            {"type": "text", "text": "Describe what's in this image."},
            {"type": "text", "text": "Then, describe this dog."},
            {
                "type": "image_url",
                "image_url": {
                    "url": "https://images.unsplash.com/photo-1518717758536-85ae29035b6d"
                }
            },
            {"type": "text", "text": "What are the main differences between them?"}
        ]
    }
]
```

By running this code:

```python
# coding=utf-8
from __future__ import print_function
from chat_completions_conversation import ChatCompletionsConversation

# Initialize conversation
conv = ChatCompletionsConversation(
    api_key=u'...',
    base_url=u'https://api.openai.com/v1',
    model=u'gpt-4.1'
)

# Load conversation
conv.load_from_json_file(u'messages.json')

# Add a message to the model's message list without obtaining a response
conv.append_user_message(u'Also give me subjective feedback regarding the images.')

# Print messages
print(u'Messages: """', end=u'')
print(conv.export_to_text(), end=u'')
print(u'"""')
print()

# Create message and stream response
print(u'Assistant response: """', end=u'')
for chunk in conv.send_and_stream_response(u'Help me with the above tasks.'):
    print(chunk, end=u'')
print(u'"""')
print()

# Save conversation
conv.save_to_json_file(u'new-messages.json')

# Print messages
print(u'Messages after assistant response: """', end=u'')
print(conv.export_to_text(), end=u'')
print(u'"""')
```

we can get this output:

```
Messages: """..."""

Assistant response: """..."""

Messages after assistant response: """..."""
```

What `...` actually varies from model to model and from run to run. We embrace randomness and make ZERO effort in regularizing model output.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).

# PyChat

PyChat is a chat application built with FastAPI.

## Features

- Chat with AI models
- Chat history management
- User interface

## Environment Variables

| Variable Name | Required | Description |
|----------------|:--------:|-----------------------------------------------------------------------------|
| OPENAI_API_KEY | ✅ | OpenAI API key |
| NGINX_PORT | ✅ | Port number for access |
| ANTHROPIC_API_KEY | | Anthropic API key |

## Getting Started

### Prerequisites

- Docker

- Docker Compose

### Installation

1. Clone the repository:

```

git clone https://github.com/yourusername/PyChat.git

```

2. Navigate to the project directory:

```

cd PyChat

```

3. Create a `.env` file in the project root and set the required environment variables:

```

OPENAI_API_KEY=your_openai_api_key

NGINX_PORT=8888

```

4. Start the application:

```

docker compose up

```

This command will build the Docker image and start the containers.

5. Access the application in your web browser at `http://localhost:8888` (or the port you specified in the `.env` file).


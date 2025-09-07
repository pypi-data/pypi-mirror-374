# n8n-chat-cli

A command-line interface for n8n chat webhooks.

## Installation

You can install `n8n-chat-cli` from PyPI:

```bash
pip install n8n-chat-cli
```

## Usage

You can use the `n8n-chat` command to start a chat session.

### With a command-line argument:

```bash
n8n-chat <your_n8n_chat_webhook_url>
```

### With an environment variable:

You can set the `N8N_CHAT_URL` environment variable to your n8n chat webhook URL.

```bash
export N8N_CHAT_URL=<your_n8n_chat_webhook_url>
n8n-chat
```

Once connected, you can type your messages and press Enter. To exit, type `exit` or press `Ctrl+C`.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### Releasing a new version

To release a new version, create a new tag with the version number and push it to the repository. The workflow will then automatically create a GitHub release and publish the package to PyPI.

```bash
git tag v0.1.3
git push origin v0.1.3
```

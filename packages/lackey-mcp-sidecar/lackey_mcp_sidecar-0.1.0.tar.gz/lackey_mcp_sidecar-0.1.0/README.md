# Lackey MCP Sidecar

A FastAPI web interface for task and project management that integrates with the Lackey task management system through the Model Context Protocol (MCP).

## Features

- **Interactive Task Visualization**: Visual task graph with dependency mapping
- **Real-time Dashboard**: Live statistics and project overview
- **Task Management**: View, search, and interact with tasks across projects
- **Animated UI**: Pulsing animations for in-progress tasks for better visual distinction
- **Responsive Design**: Modern, glassmorphic UI with smooth animations
- **Copy Functionality**: Easy ID copying with toast notifications

## Installation

Install the latest release from PyPI:
```bash
pip install lackey-mcp-sidecar
```

For local development:
```bash
git clone <repository-url>
cd lackey-mcp-sidecar
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

## Usage

### Starting the Server

Start the FastAPI server:
```bash
lackey-sidecar
```

The web interface will be available at `http://localhost:8000`.

### Features Overview

- **Dashboard**: Overview of all projects and tasks with status breakdown
- **Project View**: Detailed task graph visualization with dependencies
- **Search**: Global search across all tasks and projects
- **Task Details**: Click any task to view detailed information
- **Auto-refresh**: Optional automatic data refresh every 30 seconds

## Project Structure

```
lackey-mcp-sidecar/
├── src/
│   └── lackey_mcp_sidecar/
│       ├── main.py              # FastAPI application
│       ├── static/
│       │   ├── css/main.css     # Styling
│       │   └── js/main.js       # Frontend functionality
│       └── templates/
│           └── index.html       # Main template
├── pyproject.toml              # Package configuration
├── MANIFEST.in                 # Data file inclusion
└── README.md                   # Project documentation
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI applications
- **Jinja2**: Template engine for HTML rendering
- **Lackey Core**: Task management system integration (optional)

## Development

The project follows modern web development practices:

- **Separation of Concerns**: HTML, CSS, and JavaScript are in separate files
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Glassmorphic design with smooth animations
- **Clean Code**: Well-organized and documented codebase

### File Organization

- `main.py`: Backend API endpoints and server configuration
- `static/css/main.css`: All styling including animations and responsive design
- `static/js/main.js`: Frontend JavaScript functionality
- `templates/index.html`: Clean HTML structure without inline styles/scripts

## API Documentation

For detailed API documentation including request/response examples, parameters, and error codes, see [API.md](API.md).

**Quick Reference**:
- `GET /`: Main web interface
- `GET /projects`: List all projects
- `GET /tasks/{project_id}`: Get tasks for a specific project
- `GET /task/{task_id}`: Get detailed task information
- `GET /search`: Search tasks across all projects
- `GET /dashboard-stats`: Get dashboard statistics

## Configuration

The application automatically detects and connects to a Lackey workspace if available. No additional configuration is required for basic usage.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

"""Lackey MCP Sidecar - FastAPI web interface for task/project/note management."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import logging
import os
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy external loggers
logging.getLogger('watchfiles.main').setLevel(logging.WARNING)
logging.getLogger('lackey.core').setLevel(logging.WARNING)
logging.getLogger('uvicorn.access').setLevel(logging.WARNING)


def find_lackey_workspace():
    """Find the lackey workspace by examining running processes."""
    import subprocess
    try:
        # Get only lackey processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        grep_result = subprocess.run(['grep', 'lackey'], input=result.stdout, capture_output=True, text=True)
        logger.debug(f"Lackey processes found: {len(grep_result.stdout.split())}")
        
        for line in grep_result.stdout.split('\n'):
            logger.debug(f"Checking process line: {line}")
            if 'lackey serve --workspace' in line and '.lackey' in line:
                logger.debug(f"Found lackey serve process: {line}")
                # Extract the directory where lackey is running from
                if '.venv/bin/lackey' in line:
                    # Extract path like: /path/to/.venv/bin/lackey -> /path/to/.lackey
                    parts = line.split()
                    logger.debug(f"Process line parts: {parts}")
                    for part in parts:
                        if '.venv/bin/lackey' in part:
                            base_path = part.replace('/.venv/bin/lackey', '')
                            workspace_path = f"{base_path}/.lackey"
                            logger.debug(f"Detected workspace: {workspace_path}")
                            return workspace_path
    except Exception as e:
        logger.error(f"Could not detect lackey workspace: {e}")
    logger.warning("No workspace found")
    return None

try:
    from lackey.core import LackeyCore
    from lackey.models import Task, Project, TaskStatus, ProjectStatus, Complexity
    from lackey.notes import NoteType
    logger.info("Successfully imported lackey modules")
except ImportError as e:
    logger.warning(f"Could not import lackey modules: {e}")
    LackeyCore = None

app = FastAPI(title="Lackey MCP Sidecar", description="Web interface for Lackey task management")

# Template setup
import os
from pathlib import Path

template_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

# Mount static files from static directory
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(template_dir))

# Initialize lackey core if available
lackey_core = None
if LackeyCore:
    try:
        workspace_path = find_lackey_workspace()
        if workspace_path:
            lackey_core = LackeyCore(workspace_path)
            logger.debug(f"Initialized LackeyCore with workspace: {workspace_path}")
        else:
            logger.warning("Could not detect lackey workspace from running processes")
    except Exception as e:
        logger.error(f"Could not initialize LackeyCore: {e}")

# API Routes
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/search")
async def search_tasks(q: str = "", project_id: str = None, status: str = None, complexity: str = None):
    """Global search endpoint for tasks across all projects."""
    try:
        workspace_path = find_lackey_workspace()
        if not workspace_path:
            return {"results": [], "total": 0, "query": q}
        
        # Import search modules
        from lackey.advanced_search import AdvancedSearchEngine, QueryBuilder
        from lackey.storage import LackeyStorage
        
        # Initialize search engine
        storage = LackeyStorage(workspace_path)
        search_engine = AdvancedSearchEngine(storage, workspace_path)
        
        # Build search query
        query_builder = QueryBuilder()
        
        if q:
            query_builder.text(q)
        
        if status:
            from lackey.models import TaskStatus
            try:
                task_status = TaskStatus(status)
                query_builder.filter_by_status(task_status)
            except ValueError:
                pass
        
        if complexity:
            from lackey.models import Complexity
            try:
                task_complexity = Complexity(complexity)
                query_builder.filter_by_complexity(task_complexity)
            except ValueError:
                pass
        
        # Execute search
        search_query = query_builder.build()
        results = search_engine.search(search_query, project_id)
        
        # Format results for API
        formatted_results = []
        for project_id, task in results.tasks:
            formatted_results.append({
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "complexity": task.complexity.value,
                "project_id": project_id,
                "created": task.created.isoformat() if task.created else None,
                "updated": task.updated.isoformat() if task.updated else None,
                "tags": task.tags,
                "assigned_to": task.assigned_to
            })
        
        return {
            "results": formatted_results,
            "total": results.total_count,
            "query": q,
            "facets": results.facets,
            "execution_time_ms": results.execution_time_ms
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"results": [], "total": 0, "query": q, "error": str(e)}

@app.get("/dashboard-stats")
async def get_dashboard_stats():
    """Get dashboard statistics for the landing page."""
    try:
        workspace_path = find_lackey_workspace()
        if not workspace_path:
            return {
                "total_tasks": 0,
                "active_projects": 0,
                "total_projects": 0,
                "workspace_connected": False,
                "task_status_breakdown": {},
                "recent_activity": []
            }
        
        import yaml
        index_file = os.path.join(workspace_path, "index.yaml")
        if not os.path.exists(index_file):
            return {
                "total_tasks": 0,
                "active_projects": 0,
                "total_projects": 0,
                "workspace_connected": True,
                "task_status_breakdown": {},
                "recent_activity": []
            }
            
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
            projects = index_data.get('projects', [])
            task_to_project = index_data.get('task_to_project', {})
        
        # Calculate stats
        total_tasks = len(task_to_project)
        total_projects = len(projects)
        active_projects = sum(1 for p in projects if p.get('task_count', 0) > p.get('completed_count', 0))
        
        # Task status breakdown
        task_status_breakdown = {"todo": 0, "in_progress": 0, "done": 0, "blocked": 0}
        recent_tasks = []
        
        # Analyze all tasks for status breakdown and recent activity
        for task_id, project_id in task_to_project.items():
            task_file = os.path.join(workspace_path, "projects", project_id, "tasks", f"{task_id}.md")
            if os.path.exists(task_file):
                try:
                    with open(task_file, 'r') as tf:
                        content = tf.read()
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 2:
                                frontmatter = yaml.safe_load(parts[1])
                                status = frontmatter.get("status", "todo").replace("-", "_")
                                if status in task_status_breakdown:
                                    task_status_breakdown[status] += 1
                                
                                # Collect recent tasks (with updated timestamp)
                                updated = frontmatter.get("updated")
                                if updated:
                                    recent_tasks.append({
                                        "id": task_id,
                                        "title": frontmatter.get("title", "Untitled"),
                                        "project_id": project_id,
                                        "updated": updated,
                                        "status": status
                                    })
                except Exception as e:
                    logger.warning(f"Error reading task {task_id}: {e}")
        
        # Sort recent tasks by updated time and take top 5
        recent_tasks.sort(key=lambda x: x["updated"], reverse=True)
        recent_activity = recent_tasks[:5]
        
        return {
            "total_tasks": total_tasks,
            "active_projects": active_projects,
            "total_projects": total_projects,
            "workspace_connected": True,
            "task_status_breakdown": task_status_breakdown,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {e}")
        return {
            "total_tasks": 0,
            "active_projects": 0,
            "total_projects": 0,
            "workspace_connected": False,
            "task_status_breakdown": {},
            "recent_activity": [],
            "error": str(e)
        }

@app.get("/projects")
async def get_projects():
    try:
        workspace_path = find_lackey_workspace()
        logger.debug(f"Workspace path from detection: {workspace_path}")
        if not workspace_path:
            logger.warning("No workspace path found")
            return []
        
        import yaml
        index_file = os.path.join(workspace_path, "index.yaml")
        logger.debug(f"Looking for index file at: {index_file}")
        if os.path.exists(index_file):
            logger.debug("Index file exists, reading...")
            with open(index_file, 'r') as f:
                index_data = yaml.safe_load(f)
                projects = index_data.get('projects', [])
                logger.debug(f"Found {len(projects)} projects")
                return [{"id": p["id"], "name": p["name"], "status": p.get("status", "unknown"), 
                        "task_count": p.get("task_count", 0), "completed_count": p.get("completed_count", 0)} 
                       for p in projects]
        else:
            logger.warning("Index file does not exist")
        return []
    except Exception as e:
        logger.error(f"Error in get_projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{project_id}")
async def get_tasks_for_project(project_id: str):
    try:
        workspace_path = find_lackey_workspace()
        logger.debug(f"Workspace path: {workspace_path}")
        if not workspace_path:
            return []
        
        import yaml
        index_file = os.path.join(workspace_path, "index.yaml")
        if not os.path.exists(index_file):
            logger.warning(f"Index file not found: {index_file}")
            return []
            
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
            task_to_project = index_data.get('task_to_project', {})
            
        logger.debug(f"Looking for tasks in project: {project_id}")
        logger.debug(f"Found {len(task_to_project)} total task mappings")
            
        # Find tasks for this project
        project_tasks = []
        task_titles = {}  # Map task IDs to titles for dependency display
        
        for task_id, proj_id in task_to_project.items():
            if proj_id == project_id:
                logger.debug(f"Found task {task_id} for project {project_id}")
                # Read task file
                task_file = os.path.join(workspace_path, "projects", project_id, "tasks", f"{task_id}.md")
                if os.path.exists(task_file):
                    with open(task_file, 'r') as tf:
                        content = tf.read()
                        # Parse YAML frontmatter
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 2:
                                frontmatter = yaml.safe_load(parts[1])
                                dependencies = frontmatter.get("dependencies", [])
                                logger.debug(f"Task {task_id} has dependencies: {dependencies}")
                                task_data = {
                                    "id": frontmatter.get("id", task_id),
                                    "title": frontmatter.get("title", "Untitled"),
                                    "status": frontmatter.get("status", "unknown"),
                                    "complexity": frontmatter.get("complexity", "medium"),
                                    "dependencies": dependencies
                                }
                                project_tasks.append(task_data)
                                task_titles[task_id] = task_data["title"]
                else:
                    logger.warning(f"Task file not found: {task_file}")
        
        logger.debug(f"Found {len(project_tasks)} tasks for project {project_id}")
        
        # Add dependency titles for display
        for task in project_tasks:
            task["dependency_titles"] = [task_titles.get(dep_id, dep_id) for dep_id in task["dependencies"]]
            logger.debug(f"Task {task['id']} dependency titles: {task['dependency_titles']}")
        
        return project_tasks
    except Exception as e:
        logger.error(f"Error in get_tasks_for_project: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/task/{task_id}")
async def get_task_details(task_id: str):
    try:
        workspace_path = find_lackey_workspace()
        if not workspace_path:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        import yaml
        index_file = os.path.join(workspace_path, "index.yaml")
        if not os.path.exists(index_file):
            raise HTTPException(status_code=404, detail="Index not found")
            
        with open(index_file, 'r') as f:
            index_data = yaml.safe_load(f)
            task_to_project = index_data.get('task_to_project', {})
            
        project_id = task_to_project.get(task_id)
        if not project_id:
            raise HTTPException(status_code=404, detail="Task not found")
            
        task_file = os.path.join(workspace_path, "projects", project_id, "tasks", f"{task_id}.md")
        if not os.path.exists(task_file):
            raise HTTPException(status_code=404, detail="Task file not found")
            
        # Get task notes
        notes_dir = os.path.join(workspace_path, "projects", project_id, "tasks", task_id, "notes")
        notes = []
        logger.debug(f"Looking for notes in: {notes_dir}")
        if os.path.exists(notes_dir):
            note_files = os.listdir(notes_dir)
            logger.debug(f"Found note files: {note_files}")
            for note_file in note_files:
                if note_file.endswith('.md'):
                    note_path = os.path.join(notes_dir, note_file)
                    logger.debug(f"Processing note file: {note_path}")
                    
                    # Get file modification time as fallback timestamp
                    file_mtime = os.path.getmtime(note_path)
                    file_timestamp = datetime.fromtimestamp(file_mtime).isoformat()
                    
                    with open(note_path, 'r') as nf:
                        note_content = nf.read()
                        logger.debug(f"Note content preview: {note_content[:100]}...")
                        
                        if note_content.startswith('---'):
                            note_parts = note_content.split('---', 2)
                            if len(note_parts) >= 3:
                                note_frontmatter = yaml.safe_load(note_parts[1])
                                logger.debug(f"Note frontmatter: {note_frontmatter}")
                                # Use frontmatter created date if available, otherwise use file timestamp
                                created_date = note_frontmatter.get("created", file_timestamp)
                                notes.append({
                                    "id": note_frontmatter.get("id", note_file),
                                    "content": note_parts[2].strip(),
                                    "created": created_date
                                })
                        else:
                            # Handle notes without frontmatter - use file timestamp
                            logger.debug(f"Note without frontmatter, using filename as ID and file timestamp")
                            notes.append({
                                "id": note_file,
                                "content": note_content.strip(),
                                "created": file_timestamp
                            })
        else:
            logger.debug(f"Notes directory does not exist: {notes_dir}")
        
        # Sort notes by created timestamp (oldest first)
        notes.sort(key=lambda note: note.get('created', ''))
        
        logger.debug(f"Total notes found for task {task_id}: {len(notes)}")
        
        with open(task_file, 'r') as tf:
            content = tf.read()
            
            # Get file timestamps as fallback
            file_mtime = os.path.getmtime(task_file)
            file_timestamp = datetime.fromtimestamp(file_mtime).isoformat()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    logger.debug(f"Retrieved task details for {task_id}")
                    
                    # Use frontmatter dates if available, otherwise use file timestamp
                    created_date = frontmatter.get("created", file_timestamp)
                    updated_date = frontmatter.get("updated", file_timestamp)
                    
                    return {
                        "id": frontmatter.get("id", task_id),
                        "title": frontmatter.get("title", "Untitled"),
                        "status": frontmatter.get("status", "unknown"),
                        "complexity": frontmatter.get("complexity", "medium"),
                        "created": created_date,
                        "updated": updated_date,
                        "dependencies": frontmatter.get("dependencies", []),
                        "body": body,
                        "notes": notes
                    }
        
        raise HTTPException(status_code=404, detail="Invalid task format")
    except Exception as e:
        logger.error(f"Error in get_task_details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/execution-history")
async def get_execution_history():
    """Get execution history analytics data."""
    try:
        workspace_path = find_lackey_workspace()
        logger.debug(f"Workspace path from detection: {workspace_path}")
        if not workspace_path:
            logger.warning("No workspace path found")
            return {}
        
        import yaml
        analytics_file = os.path.join(workspace_path, "analytics", "execution_history.yaml")
        logger.debug(f"Looking for execution history at: {analytics_file}")
        
        if os.path.exists(analytics_file):
            logger.debug("Execution history file exists, reading...")
            with open(analytics_file, 'r') as f:
                execution_data = yaml.safe_load(f)
                logger.debug(f"Loaded execution history with {len(execution_data)} entries")
                return execution_data
        else:
            logger.warning("Execution history file does not exist")
            return {}
    except Exception as e:
        logger.error(f"Error in get_execution_history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Entry point for the lackey-sidecar command."""
    import uvicorn
    uvicorn.run("lackey_mcp_sidecar.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()

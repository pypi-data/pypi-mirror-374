// Projects.js - Project loading, selection handling, and project metadata

async function loadProjects() {
    console.log('loadProjects called');
    try {
        console.log('Making fetch request to /projects');
        const response = await fetch('/projects');
        console.log('Projects response:', response.status);
        const projects = await response.json();
        console.log('Projects data:', projects);
        
        const dropdown = $('#projectSelect');
        const currentSelection = dropdown.val(); // Preserve current selection
        console.log('Current selection:', currentSelection);
        console.log('Dropdown element found:', dropdown.length > 0);
        dropdown.empty().append('<option value="">Select a project...</option>');
        
        if (projects.length === 0) {
            dropdown.append('<option value="" disabled>No projects found</option>');
            console.log('No projects found');
            return;
        }
        
        projects.forEach(p => {
            const option = `<option value="${p.id}">${p.name} (${p.completed_count}/${p.task_count})</option>`;
            console.log('Adding option:', option);
            dropdown.append(option);
        });
        
        // Restore previous selection
        if (currentSelection) {
            dropdown.val(currentSelection);
            console.log('Restored selection:', currentSelection);
        }
        
        // Store project data for later use
        window.projectData = {};
        projects.forEach(p => {
            window.projectData[p.id] = p;
        });
        
        console.log(`Loaded ${projects.length} projects`);
        console.log('Final dropdown HTML:', dropdown.html());
        
    } catch (error) {
        console.error('Error loading projects:', error);
        $('#projectSelect').empty().append('<option value="" disabled>Error loading projects</option>');
    }
}

// Handle project selection
$('#projectSelect').on('change', function() {
    const projectId = $(this).val();
    if (projectId && window.projectData[projectId]) {
        const project = window.projectData[projectId];
        selectProject(projectId, project.name, project.status, project.task_count, project.completed_count);
    } else {
        // Clear selection - show dashboard
        showDashboard();
    }
});

function selectProject(projectId, projectName, projectStatus, taskCount, completedCount) {
    selectedProject = projectId;
    
    // Show project ID
    $('#projectIdValue').text(projectId);
    $('#projectId').show();
    
    // Show project details in header
    $('#projectDescription').text(`${completedCount}/${taskCount} tasks`);
    $('#projectStatus').text(projectStatus);
    $('#projectMeta').show();
    
    // Load tasks for this project
    loadTasks(projectId);
}

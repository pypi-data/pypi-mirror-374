// App.js - Initialization, global variables, and utility functions

// Global variables
let selectedProject = null;
let refreshInterval = null;
let searchTimeout = null;

// Test basic functionality
console.log('Testing jQuery:', typeof $);

// Auto-load projects on page load
$(document).ready(function() {
    console.log('jQuery ready - DOM loaded');
    console.log('Dropdown element exists:', $('#projectSelect').length > 0);
    loadProjects();
    loadDashboardStats();
    setupAutoRefresh();
    setupGlobalSearch();
    setupHomeButton();
    setupReportsButton();
    setupCreateButton();
});

// Setup home button functionality
function setupHomeButton() {
    $('#homeBtn').click(function() {
        // Clear project selection
        $('#projectSelect').val('');
        
        // Explicitly clear project ID and metadata
        $('#projectId').hide();
        $('#projectIdValue').text('');
        $('#projectMeta').hide();
        
        // Show dashboard
        showDashboard();
    });
}

// Setup reports button functionality
function setupReportsButton() {
    $('#reportsBtn').click(function() {
        // Clear project selection
        $('#projectSelect').val('');
        
        // Explicitly clear project ID and metadata
        $('#projectId').hide();
        $('#projectIdValue').text('');
        $('#projectMeta').hide();
        
        // Show reports view
        showReportsView();
    });
}

// Setup auto-refresh functionality
function setupAutoRefresh() {
    const checkbox = $('#autoRefresh');
    
    function startAutoRefresh() {
        if (refreshInterval) clearInterval(refreshInterval);
        refreshInterval = setInterval(() => {
            if (selectedProject) {
                loadTasks(selectedProject);
            } else {
                loadDashboardStats();
            }
            loadProjects();
        }, 30000);
    }
    
    function stopAutoRefresh() {
        if (refreshInterval) {
            clearInterval(refreshInterval);
            refreshInterval = null;
        }
    }
    
    checkbox.on('change', function() {
        if (this.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Start auto-refresh if enabled
    if (checkbox.is(':checked')) {
        startAutoRefresh();
    }
}

// Setup create button functionality
function setupCreateButton() {
    // Handle Add Project action
    $('#addProjectBtn').click(function(e) {
        e.preventDefault();
        console.log('Add Project clicked - opening create project modal');
        
        // Show the create project modal
        $('#createProjectModal').modal('show');
    });
    
    // Handle Add Task action
    $('#addTaskBtn').click(function(e) {
        e.preventDefault();
        console.log('Add Task clicked - opening create task modal');
        
        // Load projects into the modal dropdown
        loadProjectsForTaskModal();
        
        // Show the create task modal
        $('#createTaskModal').modal('show');
    });
}

// Load projects for the task creation modal
async function loadProjectsForTaskModal() {
    try {
        const response = await fetch('/projects');
        const projects = await response.json();
        
        const select = $('#taskProjectId');
        select.empty();
        select.append('<option value="">Select a project...</option>');
        
        projects.forEach(project => {
            select.append(`<option value="${project.id}">${project.name}</option>`);
        });
        
    } catch (error) {
        console.error('Error loading projects for modal:', error);
    }
}

// Add a new step input
function addStep() {
    const container = $('#stepsContainer');
    const stepHtml = `
        <div class="input-group mb-2">
            <input type="text" class="form-control step-input" placeholder="Enter step description">
            <button class="btn btn-outline-light" type="button" onclick="removeStep(this)">✕</button>
        </div>
    `;
    container.append(stepHtml);
}

// Remove a step input
function removeStep(button) {
    $(button).closest('.input-group').remove();
}

// Add a new success criteria input
function addCriteria() {
    const container = $('#criteriaContainer');
    const criteriaHtml = `
        <div class="input-group mb-2">
            <input type="text" class="form-control criteria-input" placeholder="Enter success criteria">
            <button class="btn btn-outline-light" type="button" onclick="removeCriteria(this)">✕</button>
        </div>
    `;
    container.append(criteriaHtml);
}

// Remove a success criteria input
function removeCriteria(button) {
    $(button).closest('.input-group').remove();
}

// Submit the create task form
function submitCreateTask() {
    const form = $('#createTaskForm');
    
    // Validate required fields
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // Collect form data
    const taskData = {
        project_id: $('#taskProjectId').val(),
        title: $('#taskTitle').val(),
        objective: $('#taskObjective').val(),
        complexity: $('#taskComplexity').val(),
        context: $('#taskContext').val() || undefined,
        assigned_to: $('#taskAssignedTo').val() || undefined,
        tags: $('#taskTags').val() ? $('#taskTags').val().split(',').map(tag => tag.trim()) : undefined,
        dependencies: $('#taskDependencies').val() ? $('#taskDependencies').val().split(',').map(dep => dep.trim()) : undefined,
        steps: [],
        success_criteria: []
    };
    
    // Collect steps
    $('.step-input').each(function() {
        const value = $(this).val().trim();
        if (value) {
            taskData.steps.push(value);
        }
    });
    
    // Collect success criteria
    $('.criteria-input').each(function() {
        const value = $(this).val().trim();
        if (value) {
            taskData.success_criteria.push(value);
        }
    });
    
    // Use defaults if empty
    if (taskData.steps.length === 0) {
        taskData.steps = ['Complete the task'];
    }
    if (taskData.success_criteria.length === 0) {
        taskData.success_criteria = ['Task completed successfully'];
    }
    
    console.log('Creating task with data:', taskData);
    
    // TODO: Make API call to create the task
    // For now, just show success message and close modal
    showFeedback('Task Created!', 'success');
    $('#createTaskModal').modal('hide');
    
    // Reset form
    resetCreateTaskForm();
}

// Reset the create task form
function resetCreateTaskForm() {
    $('#createTaskForm')[0].reset();
    $('#taskComplexity').val('medium');
    
    // Reset steps to default
    $('#stepsContainer').html(`
        <div class="input-group mb-2">
            <input type="text" class="form-control step-input" placeholder="Complete the task" value="Complete the task">
            <button class="btn btn-outline-light" type="button" onclick="removeStep(this)">✕</button>
        </div>
    `);
    
    // Reset success criteria to default
    $('#criteriaContainer').html(`
        <div class="input-group mb-2">
            <input type="text" class="form-control criteria-input" placeholder="Task completed successfully" value="Task completed successfully">
            <button class="btn btn-outline-light" type="button" onclick="removeCriteria(this)">✕</button>
        </div>
    `);
}

// Add a new objective input
function addObjective() {
    const container = $('#objectivesContainer');
    const objectiveHtml = `
        <div class="input-group mb-2">
            <input type="text" class="form-control objective-input" placeholder="Enter project objective">
            <button class="btn btn-outline-light" type="button" onclick="removeObjective(this)">✕</button>
        </div>
    `;
    container.append(objectiveHtml);
}

// Remove an objective input
function removeObjective(button) {
    $(button).closest('.input-group').remove();
}

// Submit the create project form
function submitCreateProject() {
    const form = $('#createProjectForm');
    
    // Validate required fields
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // Collect form data
    const projectData = {
        friendly_name: $('#projectFriendlyName').val(),
        description: $('#projectDescription').val() || undefined,
        tags: $('#projectTags').val() ? $('#projectTags').val().split(',').map(tag => tag.trim()) : undefined,
        objectives: []
    };
    
    // Collect objectives
    $('.objective-input').each(function() {
        const value = $(this).val().trim();
        if (value) {
            projectData.objectives.push(value);
        }
    });
    
    // Remove objectives if empty
    if (projectData.objectives.length === 0) {
        projectData.objectives = undefined;
    }
    
    console.log('Creating project with data:', projectData);
    
    // TODO: Make API call to create the project
    // For now, just show success message and close modal
    showFeedback('Project Created!', 'success');
    $('#createProjectModal').modal('hide');
    
    // Reset form
    resetCreateProjectForm();
}

// Reset the create project form
function resetCreateProjectForm() {
    $('#createProjectForm')[0].reset();
    
    // Reset objectives to single empty input
    $('#objectivesContainer').html(`
        <div class="input-group mb-2">
            <input type="text" class="form-control objective-input" placeholder="Enter project objective">
            <button class="btn btn-outline-light" type="button" onclick="removeObjective(this)">✕</button>
        </div>
    `);
}

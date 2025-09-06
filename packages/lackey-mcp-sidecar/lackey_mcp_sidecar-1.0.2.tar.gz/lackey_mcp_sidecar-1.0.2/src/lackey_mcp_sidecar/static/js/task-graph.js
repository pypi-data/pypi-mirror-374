// Task-graph.js - Graph rendering, node positioning, and dependency drawing

async function loadTasks(projectId) {
    // Add project view class for proper scrolling behavior
    $('#tasks').removeClass('dashboard-view reports-view').addClass('project-view');
    
    $('#tasks').html('<div class="loading">Loading task graph...</div>');
    try {
        const response = await fetch(`/tasks/${projectId}`);
        const tasks = await response.json();
        
        console.log('Loaded tasks:', tasks);
        
        if (tasks.length === 0) {
            $('#tasks').html('<div class="text-center opacity-75" style="margin-top: 150px;">No tasks found</div>');
            return;
        }
        
        renderTaskGraph(tasks);
    } catch (error) {
        console.error('Error loading tasks:', error);
        $('#tasks').html('<div class="text-center opacity-75" style="margin-top: 150px;">🌼 Oopsie daisies - we cannot connect to lackey data...</div>');
        $('#projectMeta').hide();
    }
}

function renderTaskGraph(tasks) {
    const container = $('#tasks');
    container.empty();
    
    // Create SVG in the arrow overlay layer (dual-layer architecture)
    const arrowOverlay = $('#arrow-overlay');
    arrowOverlay.empty(); // Clear existing arrows from previous project
    const svg = $(`
        <svg class="dependency-svg" style="position: absolute; top: 0; left: 0; pointer-events: none; z-index: 1; overflow: visible;">
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="10" 
                        refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
                    <path d="M0,0 L0,6 L9,3 z" fill="rgba(255, 255, 255, 0.8)" />
                </marker>
            </defs>
        </svg>
    `);
    arrowOverlay.append(svg);
    
    // Simple layout algorithm - arrange in columns by dependency depth
    const taskMap = {};
    tasks.forEach(task => taskMap[task.id] = task);
    
    // Calculate dependency depth for each task
    const depths = {};
    const visited = new Set();
    
    function calculateDepth(taskId) {
        if (visited.has(taskId)) return depths[taskId] || 0;
        visited.add(taskId);
        
        const task = taskMap[taskId];
        if (!task || !task.dependencies || task.dependencies.length === 0) {
            depths[taskId] = 0;
            return 0;
        }
        
        let maxDepth = 0;
        task.dependencies.forEach(depId => {
            if (taskMap[depId]) {
                maxDepth = Math.max(maxDepth, calculateDepth(depId) + 1);
            }
        });
        
        depths[taskId] = maxDepth;
        return maxDepth;
    }
    
    tasks.forEach(task => calculateDepth(task.id));
    
    // Smart compact positioning with arrow corridor consideration
    const positions = {};
    const nodeWidth = 200;
    const nodeHeight = 100;
    const columnWidth = 240;  // Slightly wider for arrow corridors
    const verticalSpacing = 120;
    const startX = 50;
    const startY = 50;
    
    // Group tasks by dependency depth and relationship clusters
    const maxDepth = Math.max(...Object.values(depths));
    const columns = {};
    for (let i = 0; i <= maxDepth; i++) {
        columns[i] = [];
    }
    
    tasks.forEach(task => {
        const depth = depths[task.id] || 0;
        columns[depth].push(task);
    });
    
    // Within each column, group tasks by dependency relationships
    Object.keys(columns).forEach(depth => {
        const depthNum = parseInt(depth);
        const tasksInColumn = columns[depth];
        
        // Sort tasks to group related dependencies together
        tasksInColumn.sort((a, b) => {
            // Tasks with shared dependencies should be near each other
            const aDepCount = (a.dependencies || []).length;
            const bDepCount = (b.dependencies || []).length;
            
            // First by dependency count, then by ID for consistency
            if (aDepCount !== bDepCount) {
                return bDepCount - aDepCount; // More dependencies first
            }
            return a.id.localeCompare(b.id);
        });
        
        const x = startX + (depthNum * columnWidth);
        
        tasksInColumn.forEach((task, index) => {
            const y = startY + (index * verticalSpacing);
            positions[task.id] = { x, y };
        });
    });
    
    // Create DOM nodes
    let maxX = 0, maxY = 0;
    tasks.forEach(task => {
        const pos = positions[task.id];
        maxX = Math.max(maxX, pos.x + 200);
        maxY = Math.max(maxY, pos.y + 100);
        
        const statusClass = `status-${task.status.replace('_', '-')}`;
        const statusEmoji = {
            'todo': '📋',
            'in-progress': '⚡',
            'done': '✅',
            'blocked': '🚫'
        }[task.status.replace('_', '-')] || '📋';
        
        const node = $(`
            <div class="task-node ${statusClass}" 
                 style="left: ${pos.x}px; top: ${pos.y}px; z-index: 15;"
                 data-task-id="${task.id}">
                <div class="task-node-title">${task.title}</div>
                <div class="task-node-meta">
                    <div>${statusEmoji} ${task.status}</div>
                    <div>Complexity: ${task.complexity}</div>
                </div>
            </div>
        `);
        
        node.click(() => showTaskDetails(task.id));
        container.append(node);
    });
    
    // Draw dependency lines with smart routing and hover effects
    setTimeout(() => {
        tasks.forEach(task => {
            if (task.dependencies && task.dependencies.length > 0) {
                task.dependencies.forEach(depId => {
                    if (positions[depId] && positions[task.id]) {
                        const from = positions[depId];
                        const to = positions[task.id];
                        
                        // Connection points
                        const x1 = from.x + nodeWidth;    // Right edge of source
                        const y1 = from.y + nodeHeight/2; // Middle of source
                        const x2 = to.x;                  // Left edge of target
                        const y2 = to.y + nodeHeight/2;   // Middle of target
                        
                        // Smart routing that goes around boxes
                        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                        
                        const horizontalGap = x2 - x1;
                        const verticalGap = y2 - y1;
                        
                        // Route around boxes by going further out horizontally
                        const routingOffset = 40; // Extra space to avoid boxes
                        const cp1x = x1 + Math.max(horizontalGap * 0.3, 80) + routingOffset;
                        const cp2x = x2 - Math.max(horizontalGap * 0.3, 80) - routingOffset;
                        
                        // Vertical routing to avoid crossing boxes
                        let cp1y = y1;
                        let cp2y = y2;
                        
                        // If there's significant vertical separation, route around
                        if (Math.abs(verticalGap) > nodeHeight) {
                            if (verticalGap > 0) {
                                // Target is below - route above or below based on space
                                cp1y = y1 - routingOffset;
                                cp2y = y2 - routingOffset;
                            } else {
                                // Target is above
                                cp1y = y1 + routingOffset;
                                cp2y = y2 + routingOffset;
                            }
                        }
                        
                        const pathData = `M ${x1} ${y1} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`;
                        
                        path.setAttribute('d', pathData);
                        path.setAttribute('stroke', 'rgba(255, 255, 255, 0.4)'); // More subtle by default
                        path.setAttribute('stroke-width', '2');
                        path.setAttribute('fill', 'none');
                        path.setAttribute('marker-end', 'url(#arrowhead)');
                        path.setAttribute('class', 'dependency-arrow');
                        path.setAttribute('data-from', depId);
                        path.setAttribute('data-to', task.id);
                        
                        // Add transition for smooth hover effects
                        path.style.transition = 'stroke 0.2s ease, stroke-width 0.2s ease';
                        
                        svg[0].appendChild(path);
                    }
                });
            }
        });
        
        // Add hover effects to tasks and arrows
        $('.task-node').hover(
            function() {
                const taskId = $(this).data('task-id');
                
                // Fade out all arrows
                $('.dependency-arrow').css({
                    'stroke': 'rgba(255, 255, 255, 0.1)',
                    'stroke-width': '1'
                });
                
                // Highlight arrows connected to this task
                $(`.dependency-arrow[data-from="${taskId}"], .dependency-arrow[data-to="${taskId}"]`).css({
                    'stroke': 'rgba(255, 255, 255, 0.9)',
                    'stroke-width': '3'
                });
                
                // Highlight the task itself
                $(this).css('transform', 'scale(1.02)');
            },
            function() {
                // Reset all arrows
                $('.dependency-arrow').css({
                    'stroke': 'rgba(255, 255, 255, 0.4)',
                    'stroke-width': '2'
                });
                
                // Reset task scale
                $(this).css('transform', 'scale(1)');
            }
        );
    }, 100);
    
    // Set SVG dimensions to cover full content area with minimal padding
    const svgWidth = maxX + 20;  // Just enough padding for arrows and borders
    const svgHeight = maxY + 20; // Just enough padding for arrows and borders
    svg.attr('width', svgWidth).attr('height', svgHeight);
    
    // Set container height to accommodate all positioned elements
    container.css('min-height', svgHeight + 'px');
    
    // Add scroll synchronization for dual-layer architecture
    const tasksContainer = $('#tasks');
    const updateArrowPosition = () => {
        const scrollLeft = tasksContainer.scrollLeft();
        const scrollTop = tasksContainer.scrollTop();
        svg.css('transform', `translate(${-scrollLeft}px, ${-scrollTop}px)`);
    };
    
    // Sync arrows with scroll position
    tasksContainer.on('scroll', updateArrowPosition);
    updateArrowPosition(); // Initial position
}

async function showTaskDetails(taskId) {
    try {
        const response = await fetch(`/task/${taskId}`);
        const task = await response.json();
        
        $('#taskModalTitle').text(task.title);
        $('#taskModalBody').html(`
            <div class="mb-3">
                <span style="font-size: 1.25em; font-weight: bold;">${task.id}</span>
                <button class="btn btn-sm ms-2 p-1 copy-btn" onclick="copyToClipboard('${task.id}', this)" title="Copy ID" style="font-size: 1.25em; border: none; background: none; color: inherit;">
                    ⧉
                </button><br>
                <strong>Status:</strong> ${task.status}<br>
                <strong>Complexity:</strong> ${task.complexity}<br>
                <strong>Created:</strong> ${task.created ? new Date(task.created).toLocaleString() : 'No date'}<br>
                <strong>Updated:</strong> ${task.updated ? new Date(task.updated).toLocaleString() : 'No date'}
            </div>
            <div class="mb-3">
                <strong>Task Details:</strong>
                <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 5px; margin-top: 0.5rem;">
                    <pre style="white-space: pre-wrap; margin: 0;">${task.body}</pre>
                </div>
            </div>
            ${task.notes && task.notes.length > 0 ? `
            <div class="mb-3">
                <strong>Notes:</strong>
                ${task.notes.map(note => `
                    <div style="background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 5px; margin-top: 0.5rem;">
                        <div style="font-size: 0.8rem; opacity: 0.7; margin-bottom: 0.5rem;">
                            ${note.created ? new Date(note.created).toLocaleString() : 'No date'}
                        </div>
                        <pre style="white-space: pre-wrap; margin: 0;">${note.content}</pre>
                    </div>
                `).join('')}
            </div>
            ` : ''}
        `);
        
        new bootstrap.Modal(document.getElementById('taskModal')).show();
    } catch (error) {
        console.error('Error loading task details:', error);
    }
}

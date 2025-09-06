// Dashboard.js - Dashboard stats, connection status, activity management, and view switching

function showDashboard() {
    selectedProject = null;
    
    // Hide project metadata and ID
    $('#projectMeta').hide();
    $('#projectId').hide();
    $('#projectIdValue').text(''); // Clear the ID value
    
    // Clear dependency lines from previous project view
    $('#arrow-overlay').empty();
    
    // Add dashboard view class for proper styling
    $('#tasks').removeClass('project-view reports-view').addClass('dashboard-view');
    
    // Show dashboard stats
    $('#tasks').html(`
        <div id="dashboardStats" class="dashboard-stats">
            <div class="dashboard-left">
                <div class="connection-status">
                    <div class="connection-dot disconnected"></div>
                    <span>Loading workspace data...</span>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="totalTasks">-</div>
                        <div class="stat-label">Total Tasks</div>
                        <div class="status-breakdown" id="statusBreakdown">
                            <div class="status-item">
                                <div class="status-dot todo"></div>
                                <span id="todoCount">-</span>
                            </div>
                            <div class="status-item">
                                <div class="status-dot in-progress"></div>
                                <span id="inProgressCount">-</span>
                            </div>
                            <div class="status-item">
                                <div class="status-dot done"></div>
                                <span id="doneCount">-</span>
                            </div>
                            <div class="status-item">
                                <div class="status-dot blocked"></div>
                                <span id="blockedCount">-</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="stat-number" id="activeProjects">-</div>
                        <div class="stat-label">Active Projects</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; opacity: 0.7;">
                            <span id="totalProjects">-</span> total projects
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-right">
                <div class="recent-activity" id="recentActivity" style="display: none;">
                    <h3>Recent Activity</h3>
                    <div id="activityList"></div>
                </div>
            </div>
        </div>
    `);
    
    loadDashboardStats();
}

async function loadDashboardStats() {
    try {
        const response = await fetch('/dashboard-stats');
        const stats = await response.json();
        
        // Update connection status
        const connectionStatus = $('.connection-status');
        const connectionDot = connectionStatus.find('.connection-dot');
        const connectionText = connectionStatus.find('span');
        
        if (stats.workspace_connected) {
            connectionDot.removeClass('disconnected').addClass('connected');
            connectionText.text('Workspace Connected');
        } else {
            connectionDot.removeClass('connected').addClass('disconnected');
            connectionText.text('Workspace Disconnected');
        }
        
        // Update stats
        $('#totalTasks').text(stats.total_tasks);
        $('#activeProjects').text(stats.active_projects);
        $('#totalProjects').text(stats.total_projects);
        
        // Update status breakdown
        $('#todoCount').text(stats.task_status_breakdown.todo || 0);
        $('#inProgressCount').text(stats.task_status_breakdown.in_progress || 0);
        $('#doneCount').text(stats.task_status_breakdown.done || 0);
        $('#blockedCount').text(stats.task_status_breakdown.blocked || 0);
        
        // Update recent activity
        if (stats.recent_activity && stats.recent_activity.length > 0) {
            const activityHtml = stats.recent_activity.map(activity => `
                <div class="activity-item status-${activity.status}" data-task-id="${activity.id}" data-project-id="${activity.project_id}">
                    <div>
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-meta">Project: ${activity.project_id}</div>
                    </div>
                    <div class="activity-meta">
                        ${new Date(activity.updated).toLocaleDateString()}
                    </div>
                </div>
            `).join('');
            
            $('#activityList').html(activityHtml);
            $('#recentActivity').show();
            
            // Make activity items clickable
            $('.activity-item').click(function() {
                const taskId = $(this).data('task-id');
                const projectId = $(this).data('project-id');
                
                // Switch to the project and show task details
                $('#projectSelect').val(projectId).trigger('change');
                setTimeout(() => showTaskDetails(taskId), 500);
            });
        } else {
            $('#recentActivity').hide();
        }
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        
        // Show error state
        const connectionStatus = $('.connection-status');
        const connectionDot = connectionStatus.find('.connection-dot');
        const connectionText = connectionStatus.find('span');
        
        connectionDot.removeClass('connected').addClass('disconnected');
        connectionText.text('Error loading workspace data');
    }
}

// Show reports view
function showReportsView() {
    selectedProject = null;
    
    // Hide project metadata and ID
    $('#projectMeta').hide();
    $('#projectId').hide();
    $('#projectIdValue').text('');
    
    // Clear dependency lines from previous project view
    $('#arrow-overlay').empty();
    
    // Add reports view class for proper styling
    $('#tasks').removeClass('project-view dashboard-view').addClass('reports-view');
    
    // Show reports view
    $('#tasks').html(`
        <div id="reportsView" class="reports-view">
            <div class="reports-content">
                <div class="row">
                    <div class="col-md-6 mb-4">
                        <div class="report-card">
                            <div class="report-card-header">
                                <h4>💰 Strands Cost Analytics</h4>
                            </div>
                            <div class="report-card-body">
                                <div id="costAnalytics" class="metrics-grid">
                                    <div class="loading">Loading cost data...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6 mb-4">
                        <div class="report-card">
                            <div class="report-card-header">
                                <h4>🚀 Strands Performance Metrics</h4>
                            </div>
                            <div class="report-card-body">
                                <div id="performanceMetrics" class="metrics-grid">
                                    <div class="loading">Loading performance data...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12 mb-4">
                        <div class="report-card">
                            <div class="report-card-header">
                                <h3>⚡ Strands Execution History</h3>
                                <p>Recent AI task execution performance and costs</p>
                            </div>
                            <div class="report-card-body">
                                <div id="executionHistoryChart" class="chart-container">
                                    <div class="loading">Loading execution data...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `);
    
    // Load execution history data
    loadExecutionHistory();
}

// Load and display execution history analytics
async function loadExecutionHistory() {
    try {
        const response = await fetch('/execution-history');
        const data = await response.json();
        
        console.log('Execution history data:', data);
        
        if (!data.executions || data.executions.length === 0) {
            $('#executionHistoryChart').html('<div class="no-data">No execution history available</div>');
            $('#costAnalytics').html('<div class="no-data">No cost data available</div>');
            $('#performanceMetrics').html('<div class="no-data">No performance data available</div>');
            return;
        }
        
        renderExecutionChart(data.executions);
        renderCostAnalytics(data.executions);
        renderPerformanceMetrics(data.executions);
        
    } catch (error) {
        console.error('Error loading execution history:', error);
        $('#executionHistoryChart').html('<div class="error">Error loading execution data</div>');
        $('#costAnalytics').html('<div class="error">Error loading cost data</div>');
        $('#performanceMetrics').html('<div class="error">Error loading performance data</div>');
    }
}

// Render execution timeline chart
function renderExecutionChart(executions) {
    const chartHtml = `
        <div class="execution-timeline">
            ${executions.map(exec => {
                const date = new Date(exec.timestamp);
                const statusColor = exec.status === 'completed' ? '#4ade80' : '#ef4444';
                const executionTime = (exec.execution_time_ms / 1000).toFixed(1);
                
                return `
                    <div class="execution-item" style="border-left: 3px solid ${statusColor};">
                        <div class="execution-header">
                            <span class="execution-status" style="color: ${statusColor};">
                                ${exec.status === 'completed' ? '✅' : '❌'} ${exec.status}
                            </span>
                            <span class="execution-time">${date.toLocaleString()}</span>
                        </div>
                        <div class="execution-details">
                            <div class="execution-metric">
                                <span class="metric-label">Execution Time:</span>
                                <span class="metric-value">${executionTime}s</span>
                            </div>
                            <div class="execution-metric">
                                <span class="metric-label">Total Cost:</span>
                                <span class="metric-value">$${exec.total_cost.toFixed(4)}</span>
                            </div>
                            <div class="execution-metric">
                                <span class="metric-label">Tasks Completed:</span>
                                <span class="metric-value">${exec.completed_tasks}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    $('#executionHistoryChart').html(chartHtml);
}

// Render cost analytics
function renderCostAnalytics(executions) {
    const totalCost = executions.reduce((sum, exec) => sum + exec.total_cost, 0);
    const totalTokens = executions.reduce((sum, exec) => sum + exec.input_tokens + exec.output_tokens, 0);
    const avgCostPerExecution = totalCost / executions.length;
    
    const costHtml = `
        <div class="metrics-row">
            <div class="metric-item">
                <div class="metric-number">$${totalCost.toFixed(4)}</div>
                <div class="metric-label">Total Cost</div>
            </div>
            <div class="metric-item">
                <div class="metric-number">${totalTokens.toLocaleString()}</div>
                <div class="metric-label">Total Tokens</div>
            </div>
        </div>
        <div class="metrics-row">
            <div class="metric-item">
                <div class="metric-number">$${avgCostPerExecution.toFixed(4)}</div>
                <div class="metric-label">Avg Cost/Execution</div>
            </div>
            <div class="metric-item">
                <div class="metric-number">${executions.length}</div>
                <div class="metric-label">Total Executions</div>
            </div>
        </div>
    `;
    
    $('#costAnalytics').html(costHtml);
}

// Render performance metrics
function renderPerformanceMetrics(executions) {
    const completedExecutions = executions.filter(exec => exec.status === 'completed');
    const successRate = (completedExecutions.length / executions.length * 100).toFixed(1);
    const avgExecutionTime = completedExecutions.reduce((sum, exec) => sum + exec.execution_time_ms, 0) / completedExecutions.length;
    const totalTasksCompleted = executions.reduce((sum, exec) => sum + exec.completed_tasks, 0);
    
    const performanceHtml = `
        <div class="metrics-row">
            <div class="metric-item">
                <div class="metric-number">${successRate}%</div>
                <div class="metric-label">Success Rate</div>
            </div>
            <div class="metric-item">
                <div class="metric-number">${(avgExecutionTime / 1000).toFixed(1)}s</div>
                <div class="metric-label">Avg Execution Time</div>
            </div>
        </div>
        <div class="metrics-row">
            <div class="metric-item">
                <div class="metric-number">${totalTasksCompleted}</div>
                <div class="metric-label">Tasks Completed</div>
            </div>
            <div class="metric-item">
                <div class="metric-number">${completedExecutions.length}</div>
                <div class="metric-label">Successful Runs</div>
            </div>
        </div>
    `;
    
    $('#performanceMetrics').html(performanceHtml);
}

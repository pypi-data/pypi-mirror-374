// Search.js - Search functionality, results display, and filtering

function setupGlobalSearch() {
    const searchInput = $('#globalSearch');
    const searchBtn = $('#searchBtn');
    let searchResults = null;
    
    function performSearch(query) {
        if (!query.trim()) {
            hideSearchResults();
            return;
        }
        
        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                showSearchResults(data.results, query);
            })
            .catch(error => {
                console.error('Search error:', error);
                hideSearchResults();
            });
    }
    
    function showSearchResults(results, query) {
        hideSearchResults();
        
        if (results.length === 0) {
            searchResults = $(`
                <div class="search-results">
                    <div class="search-result-item">
                        <div class="search-result-title">No results found</div>
                        <div class="search-result-meta">Try a different search term</div>
                    </div>
                </div>
            `);
        } else {
            const resultItems = results.map(task => `
                <div class="search-result-item status-${task.status.replace('_', '-')}" data-task-id="${task.id}" data-project-id="${task.project_id}">
                    <div class="search-result-title">${task.title}</div>
                    <div class="search-result-meta">
                        ${task.status} • ${task.complexity} • Project: ${task.project_id}
                        ${task.tags.length > 0 ? ' • Tags: ' + task.tags.join(', ') : ''}
                    </div>
                </div>
            `).join('');
            
            searchResults = $(`
                <div class="search-results">
                    ${resultItems}
                </div>
            `);
            
            // Handle result clicks
            searchResults.find('.search-result-item').click(function() {
                const taskId = $(this).data('task-id');
                const projectId = $(this).data('project-id');
                
                // Switch to the project and show task details
                $('#projectSelect').val(projectId).trigger('change');
                setTimeout(() => showTaskDetails(taskId), 500);
                hideSearchResults();
                searchInput.val('');
            });
        }
        
        const inputOffset = searchInput.offset();
        searchResults.css({
            top: inputOffset.top + searchInput.outerHeight(),
            left: inputOffset.left
        });
        
        $('body').append(searchResults);
    }
    
    function hideSearchResults() {
        if (searchResults) {
            searchResults.remove();
            searchResults = null;
        }
    }
    
    // Search on input with debounce
    searchInput.on('input', function() {
        const query = $(this).val();
        
        if (searchTimeout) {
            clearTimeout(searchTimeout);
        }
        
        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 300);
    });
    
    // Search on button click
    searchBtn.click(function() {
        performSearch(searchInput.val());
    });
    
    // Search on Enter key
    searchInput.on('keypress', function(e) {
        if (e.which === 13) {
            performSearch($(this).val());
        }
    });
    
    // Hide results when clicking outside
    $(document).click(function(e) {
        if (!$(e.target).closest('.search-container').length) {
            hideSearchResults();
        }
    });
    
    // Hide results on escape
    searchInput.on('keydown', function(e) {
        if (e.which === 27) { // Escape key
            hideSearchResults();
            $(this).blur();
        }
    });
}

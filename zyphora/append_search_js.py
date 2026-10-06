import os

nav_path = r"c:\Users\dell\Documents\solar-project\Zyphora_Solar\zyphora\templates\include\topnavbar.html"

search_js = """

<!-- UNIVERSAL SEARCH SCRIPT -->
<script>
document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("universalSearchInput");
    const resultsDiv = document.getElementById("universalSearchResults");
    const resultsBody = document.getElementById("searchResultsBody");
    
    if (!searchInput) return;

    // Global hotkey Alt+S to focus search
    document.addEventListener("keydown", function(e) {
        if (e.altKey && e.key === 's') {
            e.preventDefault();
            searchInput.focus();
        }
    });

    // Close on click outside
    document.addEventListener("click", function(e) {
        if (!searchInput.contains(e.target) && !resultsDiv.contains(e.target)) {
            resultsDiv.style.display = 'none';
        }
    });

    let timeout = null;
    searchInput.addEventListener("input", function() {
        clearTimeout(timeout);
        const q = this.value.trim();
        
        if (q.length < 2) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        timeout = setTimeout(() => {
            fetch(`/crm/universal-search/?q=${encodeURIComponent(q)}`)
                .then(res => res.json())
                .then(data => {
                    resultsBody.innerHTML = '';
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            let icon = 'bi-file-earmark';
                            if (item.type === 'Lead') icon = 'bi-person';
                            if (item.type === 'Project') icon = 'bi-folder';
                            if (item.type === 'Invoice') icon = 'bi-receipt';
                            
                            resultsBody.innerHTML += `
                                <a href="${item.url}" class="dropdown-item py-2 d-flex align-items-start border-bottom">
                                    <i class="bi ${icon} fs-5 text-primary me-3 mt-1"></i>
                                    <div>
                                        <div class="fw-bold text-dark">${item.title}</div>
                                        <div class="text-muted small">${item.type} &bull; ${item.subtitle}</div>
                                    </div>
                                </a>
                            `;
                        });
                        resultsDiv.style.display = 'block';
                    } else {
                        resultsBody.innerHTML = '<div class="p-3 text-muted text-center">No results found</div>';
                        resultsDiv.style.display = 'block';
                    }
                })
                .catch(err => console.error(err));
        }, 300);
    });
});
</script>
"""

with open(nav_path, "a", encoding="utf-8") as f:
    f.write(search_js)

print("Appended JS script.")

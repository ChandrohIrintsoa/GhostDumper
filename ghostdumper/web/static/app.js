// Optimized app.js code

// Constants
const ITEMS_PER_PAGE = 50;
const VALID_FILE_EXTENSIONS = ['.so', '.dll', '.exe', '.dat'];

// Variables
let currentPage = 1;
let items = []; // Your data source

// Function to validate file extensions
function isValidFileExtension(filename) {
    return VALID_FILE_EXTENSIONS.some(ext => filename.endsWith(ext));
}

// Function to handle errors
function handleError(error) {
    console.error('Error:', error);
    alert('An error occurred: ' + error.message);
}

// Function to render items in table
function renderItems() {
    const tableBody = document.querySelector('#table-body');
    const fragment = document.createDocumentFragment();

    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const itemsToRender = items.slice(start, end);

    itemsToRender.forEach(item => {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.textContent = item.name;
        row.appendChild(cell);
        fragment.appendChild(row);
    });

    // Clear the table body and append the fragment
    tableBody.innerHTML = '';
    tableBody.appendChild(fragment);
}

// Function to handle pagination
function goToPage(page) {
    currentPage = page;
    renderItems();
}

// Event delegation for table clicks
document.querySelector('#table-body').addEventListener('click', (event) => {
    const target = event.target.closest('tr');
    if (target) {
        // Handle row click
        alert('Row clicked: ' + target.textContent);
    }
});

// Debouncing function
function debounce(func, delay) {
    let timeout;
    return function(...args) {
        if (timeout) clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

// Search function with debounce
const searchInput = document.querySelector('#search-input');
searchInput.addEventListener('input', debounce(function() {
    const query = this.value;
    // Filter items based on query
    items = items.filter(item => item.name.includes(query));
    renderItems();
}, 300));

// Load initial data (should be replaced with your actual data loading logic)
// items = loadData();
renderItems();

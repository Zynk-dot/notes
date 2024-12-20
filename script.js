// Get Elements
const consoleElement = document.getElementById('console');
const toggleConsoleBtn = document.getElementById('toggle-console-btn');
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const settingsBtn = document.getElementById('settings-btn');

// State to track console visibility
let isConsoleVisible = false;

// Open Sidebar
settingsBtn.addEventListener('click', () => {
    sidebar.classList.add('open');
    overlay.classList.add('active');
});

// Close Sidebar
overlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    overlay.classList.remove('active');
});

// Toggle Console Visibility
toggleConsoleBtn.addEventListener('click', () => {
    isConsoleVisible = !isConsoleVisible;

    if (isConsoleVisible) {
        consoleElement.classList.add('visible');
        toggleConsoleBtn.textContent = "Hide Console";
        logToConsole("Console enabled.");
    } else {
        consoleElement.classList.remove('visible');
        toggleConsoleBtn.textContent = "Show Console";
        logToConsole("Console disabled.");
    }
});

// Ensure Console Visibility Persists
document.addEventListener('DOMContentLoaded', () => {
    if (isConsoleVisible) {
        consoleElement.classList.add('visible');
    }
});

// Bulletpoint Button
document.getElementById('bulletpoint-btn').addEventListener('click', () => {
    const inputText = document.getElementById('input-box').value;
    const summary = inputText
        .split('.')
        .filter(sentence => sentence.trim())
        .map(sentence => `• ${sentence.trim()}`)
        .join('\n');
    document.getElementById('output-box').value = summary;

    // Log action to console
    logToConsole("Bulletpoint summary generated.");
});

// Summarize Button
document.getElementById('summarize-btn').addEventListener('click', () => {
    const inputText = document.getElementById('input-box').value;
    const sentences = inputText.split('.').filter(sentence => sentence.trim());
    const summary = sentences.length > 3
        ? sentences.slice(0, 3).join('. ') + '.'
        : sentences.join('. ');
    document.getElementById('output-box').value = summary;

    // Log action to console
    logToConsole("Summary generated.");
});

// Toggle Theme
document.getElementById('toggle-theme-btn').addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');

    // Log theme change to console
    logToConsole(
        `Theme toggled to ${document.body.classList.contains('dark-mode') ? 'Dark' : 'Light'} mode.`
    );
});

// Log to Console Function
function logToConsole(message) {
    const timestamp = new Date().toLocaleTimeString();
    const consoleOutput = document.getElementById('console-output');
    consoleOutput.textContent += `[${timestamp}] ${message}\n`;
}

function logToConsole(message) {
    const timestamp = new Date().toLocaleTimeString();
    const consoleOutput = document.getElementById('console-output');

    // Add the new log message
    consoleOutput.textContent += `[${timestamp}] ${message}\n`;

    // Auto-scroll to the bottom
    const consoleContainer = document.getElementById('console');
    consoleContainer.scrollTop = consoleContainer.scrollHeight;
}

function applyTheme(theme) {
  if (theme === 'dark') {
    document.body.classList.add('dark-mode');
  } else {
    document.body.classList.remove('dark-mode');
  }
}

function initThemeToggle() {
  const toggle = document.getElementById('dark-mode-toggle');
  if (!toggle) {
    return;
  }
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    toggle.checked = true;
  }
  toggle.addEventListener('change', (event) => {
    const isChecked = event.target.checked;
    const newTheme = isChecked ? 'dark' : 'light';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
  });
}

const initialTheme = localStorage.getItem('theme') || 'light';
applyTheme(initialTheme);

export { initThemeToggle };
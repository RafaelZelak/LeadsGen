// Gerenciamento do tema
export function initTheme() {
    const isDark = localStorage.getItem('darkMode') === 'true';
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    return isDark;
}

export function toggleTheme(isDark) {
    localStorage.setItem('darkMode', isDark);
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
}
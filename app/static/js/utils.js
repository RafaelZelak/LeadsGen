// Theme Toggle
export function toggleTheme(e) {
  const isDark = e.target.checked;
  document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

// Load saved theme
export function loadSavedTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.body.setAttribute('data-theme', savedTheme);
    const themeSwitch = document.getElementById('theme-switch');
    themeSwitch.checked = savedTheme === 'dark';
  } else {
    // If no saved theme, use system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.body.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    const themeSwitch = document.getElementById('theme-switch');
    themeSwitch.checked = prefersDark;
  }
}

// CNPJ Formatter
export function formatCNPJ(cnpj) {
  return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
}

// Search and Filter
export function searchCompanies(companies, searchTerm, filters) {
  let filtered = companies;

  // Apply search
  if (searchTerm) {
    searchTerm = searchTerm.toLowerCase();
    filtered = filtered.filter(company =>
      company.razaoSocial.toLowerCase().includes(searchTerm) ||
      company.nomeFantasia.toLowerCase().includes(searchTerm) ||
      company.cnpj.includes(searchTerm)
    );
  }

  // Apply location filters
  if (filters.city) {
    filtered = filtered.filter(company =>
      company.city.toLowerCase() === filters.city.toLowerCase()
    );
  }

  if (filters.state) {
    filtered = filtered.filter(company =>
      company.state.toLowerCase() === filters.state.toLowerCase()
    );
  }

  if (filters.neighborhood) {
    filtered = filtered.filter(company =>
      company.neighborhood.toLowerCase() === filters.neighborhood.toLowerCase()
    );
  }

  return filtered;
}

// Fetch Location Suggestions
export async function fetchLocationSuggestions(type, query) {
  if (!query || query.length < 2) return [];

  try {
    const response = await fetch(`https://brasilapi.com.br/api/ibge/municipios/v1/${query}`);
    const data = await response.json();

    switch(type) {
      case 'city':
        return data.map(item => item.nome);
      case 'state':
        return [...new Set(data.map(item => item.microrregiao.mesorregiao.UF.sigla))];
      default:
        return [];
    }
  } catch (error) {
    console.error('Error fetching locations:', error);
    return [];
  }
}

// Fetch Brazilian States
export async function fetchStates() {
  try {
    const response = await fetch('https://servicodados.ibge.gov.br/api/v1/localidades/estados?orderBy=nome');
    const states = await response.json();
    return states.map(state => ({
      id: state.id,
      sigla: state.sigla,
      nome: state.nome
    }));
  } catch (error) {
    console.error('Error fetching states:', error);
    return [];
  }
}

// Fetch Cities by State
export async function fetchCitiesByState(stateUF) {
  if (!stateUF) return [];
  try {
    const response = await fetch(`https://servicodados.ibge.gov.br/api/v1/localidades/estados/${stateUF}/municipios?orderBy=nome`);
    const cities = await response.json();
    return cities.map(city => ({
      id: city.id,
      nome: city.nome
    }));
  } catch (error) {
    console.error('Error fetching cities:', error);
    return [];
  }
}

// Bitrix Integration
export async function sendToBitrix(companyId, companyData) {
  try {
    const response = await fetch(`/api/companies/${companyId}/send-to-bitrix`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(companyData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send to Bitrix');
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error sending to Bitrix:', error);
    throw error;
  }
}

// Pagination
export function calculatePagination(currentPage, totalItems, itemsPerPage) {
  const totalPages = Math.ceil(totalItems / itemsPerPage);
  const start = (currentPage - 1) * itemsPerPage;
  const end = start + itemsPerPage;

  return {
    totalPages,
    start,
    end,
    currentPage: Math.min(Math.max(1, currentPage), totalPages)
  };
}

// Update filter indicator
export function updateFilterIndicator(filters) {
  const filtersToggle = document.querySelector('.filters-toggle');
  const hasActiveFilters = Object.values(filters).some(value => value.trim() !== '');

  if (hasActiveFilters) {
    filtersToggle.classList.add('has-filters');
    filtersToggle.setAttribute('title', 'Filtros ativos');
  } else {
    filtersToggle.classList.remove('has-filters');
    filtersToggle.setAttribute('title', 'Filtros');
  }
}

export function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.getElementById('notification');
    if (!notification) {
        console.error('Notification element not found!');
        return;
    }

    // Remove any existing classes and add new ones
    notification.className = 'notification';
    // Force a reflow
    void notification.offsetWidth;

    // Add the new classes
    notification.className = `notification show ${type}`;
    notification.textContent = message;

    // Clear any existing timeout
    if (notification.timeout) {
        clearTimeout(notification.timeout);
    }

    // Set new timeout
    notification.timeout = setTimeout(() => {
        notification.className = 'notification';
    }, duration);
}
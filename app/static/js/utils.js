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

// Formata o capital social para o padrão brasileiro (R$X.XXX,XX)
export function formatCapitalSocial(value) {
  if (!value) return "R$ 0,00";

  // Converte para número inteiro e garante que seja válido
  let num = parseInt(value, 10);
  if (isNaN(num)) return "R$ 0,00";

  // Formata no padrão R$ X.XXX,00
  return num.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

// Formata números de telefone para o padrão nacional
export function formatPhoneNumber(phone) {
  if (!phone) return "Não informado";

  // Remove tudo que não for número
  let digits = phone.replace(/\D/g, "");

  // Verifica se tem código de país +55
  if (digits.length === 13 && digits.startsWith("55")) {
    digits = digits.slice(2); // Remove o "55"
  }

  // Remove o 0 inicial, se houver
  if (digits.length > 2 && digits.startsWith("0")) {
    digits = digits.slice(1);
  }

  // Formatação com DDD e traço
  if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  } else if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  } else if (digits.length === 9) {
    return `${digits.slice(0, 5)}-${digits.slice(5)}`;
  } else if (digits.length === 8) {
    return `${digits.slice(0, 4)}-${digits.slice(4)}`;
  }

  // Se não for nenhum dos padrões esperados, retorna como está
  return phone;
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
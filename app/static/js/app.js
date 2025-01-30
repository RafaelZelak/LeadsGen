import { userData, fetchCompanies, fetchUserData } from './data.js';
import {
    formatCNPJ,
    toggleTheme,
    loadSavedTheme,
    fetchLocationSuggestions,
    showNotification,
    updateFilterIndicator
} from './utils.js';

// Add error handling for module loading
window.addEventListener('error', function(e) {
  console.error('Script error:', e);
  showNotification('Erro no carregamento do script: ' + e.message, 'error');
}, true);

document.addEventListener('DOMContentLoaded', async () => {
  try {
    // Carregar dados do usuário
    await fetchUserData();

    // Teste inicial da notificação
    showNotification('Aplicação inicializada', 'info', 2000);

    // Load saved theme preference
    loadSavedTheme();

    const themeSwitch = document.getElementById('theme-switch');
    const searchInput = document.getElementById('search-input');
    const companiesList = document.getElementById('companies-list');
    const filterInputs = document.querySelectorAll('.location-filter');

    if (!companiesList) {
      throw new Error('Companies list container not found');
    }

    let currentFilters = {
      city: '',
      state: '',
      neighborhood: ''
    };

    let currentPage = 1;

    // Initialize user info
    const userInfo = document.getElementById('user-info');
    if (userInfo) {
      userInfo.innerHTML = `
        <span class="user-name">${userData.name}</span>
        <span class="user-company">${userData.company}</span>
      `;
    }

    // Initialize location filters with autocomplete
    filterInputs.forEach(input => {
      let debounceTimer;
      const suggestionsList = document.createElement('ul');
      suggestionsList.className = 'suggestions-list';
      input.parentNode.appendChild(suggestionsList);

      async function showSuggestions(filterType, value = '') {
        let suggestions = [];
        if (filterType === 'state') {
          const states = await fetchStates();
          suggestions = states.map(state => state.sigla);
        } else if (filterType === 'city') {
          const stateFilter = document.querySelector('[data-filter-type="state"]').value;
          if (stateFilter) {
            const cities = await fetchCitiesByState(stateFilter);
            suggestions = cities.map(city => city.nome);
          }
        }

        if (value) {
          suggestions = suggestions.filter(item =>
            item.toLowerCase().includes(value.toLowerCase())
          );
        }

        suggestionsList.innerHTML = suggestions
          .map(suggestion => `<li>${suggestion}</li>`)
          .join('');

        suggestionsList.style.display = suggestions.length ? 'block' : 'none';
      }

      // Mostrar sugestões ao focar no input
      input.addEventListener('focus', async () => {
        await showSuggestions(input.dataset.filterType);
      });

      input.addEventListener('input', async (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
          await showSuggestions(input.dataset.filterType, e.target.value);
        }, 300);
      });

      suggestionsList.addEventListener('click', async (e) => {
        if (e.target.tagName === 'LI') {
          input.value = e.target.textContent;
          input.classList.add('has-value');
          suggestionsList.style.display = 'none';
          currentFilters[input.dataset.filterType] = e.target.textContent;

          // Se selecionou um estado, limpa a cidade
          if (input.dataset.filterType === 'state') {
            const cityInput = document.querySelector('[data-filter-type="city"]');
            cityInput.value = '';
            cityInput.classList.remove('has-value');
            currentFilters.city = '';
          }

          updateFilterIndicator(currentFilters);
        }
      });

      // Atualiza os filtros quando o valor do input muda
      input.addEventListener('change', (e) => {
        const value = e.target.value.trim();
        currentFilters[input.dataset.filterType] = value;

        if (value) {
          input.classList.add('has-value');
        } else {
          input.classList.remove('has-value');
        }

        updateFilterIndicator(currentFilters);
      });

      // Hide suggestions when clicking outside
      document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !suggestionsList.contains(e.target)) {
          suggestionsList.style.display = 'none';
        }
      });
    });

    // Add filter toggle functionality
    const filtersToggle = document.querySelector('.filters-toggle');
    const filtersContainer = document.querySelector('.filters');

    filtersToggle.addEventListener('click', () => {
      filtersToggle.classList.toggle('active');
      filtersContainer.classList.toggle('visible');
    });

    // Update filter toggle functionality to close when clicking outside
    document.addEventListener('click', (e) => {
      if (!filtersContainer.contains(e.target) &&
          !filtersToggle.contains(e.target)) {
        filtersContainer.classList.remove('visible');
        filtersToggle.classList.remove('active');
      }
    });

    // Initialize pagination
    const pagination = document.getElementById('pagination');
    const pageInput = pagination.querySelector('.page-input');
    const prevBtn = pagination.querySelector('.prev-btn');
    const nextBtn = pagination.querySelector('.next-btn');

    function updatePagination(data) {
      pageInput.value = data.current_page;
      document.querySelector('.page-total').textContent = `de ${data.pages}`;
      prevBtn.disabled = data.current_page === 1;
      nextBtn.disabled = data.current_page === data.pages;
    }

    async function updateDisplay() {
      try {
        const searchValue = searchInput.value;
        const searchOption = document.querySelector('.search-box select').value;

        let typeQuery = 'termo'; // Valor padrão

        if (searchOption === 'Cnae') {
          typeQuery = 'cnae'; // Muda o tipo para 'cnae' quando necessário
        }

        // Show loading indicator
        document.querySelector('.loading-indicator').classList.add('visible');

        const data = await fetchCompanies(currentPage, searchValue, currentFilters, typeQuery);

        updatePagination(data);
        await renderCompanies(data.items);
      } catch (error) {
        console.error('Error updating display:', error);
        // Show error to user
        showNotification('Busca de dados congestionada! Espere alguns segundos e tente novamente', 'error');
      } finally {
        // Hide loading indicator
        document.querySelector('.loading-indicator').classList.remove('visible');
      }
    }



    // Theme Toggle
    themeSwitch.addEventListener('change', toggleTheme);

    // Search Input and Button
    const searchButton = document.getElementById('search-button');

    function performSearch() {
      const searchValue = searchInput.value.trim();

      // Não faz a busca se o termo estiver vazio
      if (!searchValue) {
        showNotification('Por favor, digite algo para pesquisar', 'error', 3000);
        return;
      }

      // Atualiza os filtros com os valores atuais dos inputs
      filterInputs.forEach(input => {
        currentFilters[input.dataset.filterType] = input.value.trim();
      });

      currentPage = 1;
      updateDisplay();
    }

    // Evento de clique no botão de busca
    searchButton.addEventListener('click', performSearch);

    // Evento de pressionar Enter no campo de busca
    searchInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        performSearch();
      }
    });

    // Remove o debounce da busca automática
    searchInput.removeEventListener('input', () => {});

    // Pagination event listeners
    prevBtn.addEventListener('click', () => {
      currentPage--;
      updateDisplay();
    });

    nextBtn.addEventListener('click', () => {
      currentPage++;
      updateDisplay();
    });

    pageInput.addEventListener('focus', function() {
      this.select();
    });

    pageInput.addEventListener('blur', function() {
      currentPage = parseInt(this.value) || 1;
      updateDisplay();
    });

    pageInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        this.blur();
      }
    });

    // Initial render
    updateDisplay();
  } catch (error) {
    console.error('Error initializing application:', error);
    showNotification('Erro ao inicializar a aplicação: ' + error.message, 'error');
  }
});

async function renderCompanies(companiesList) {
  const container = document.getElementById('companies-list');
  container.innerHTML = '';

  try {
    // Primeiro, verifica todos os CNPJs de uma vez
    const cnpjs = companiesList.map(company => company.cnpj);

    const bitrixResponse = await fetch('/api/companies/check-bitrix', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        cnpjs,
        group: userData.group  // Adiciona o grupo do usuário na requisição
      })
    });

    if (!bitrixResponse.ok) {
      throw new Error('Erro ao verificar CNPJs no Bitrix');
    }

    const bitrixData = await bitrixResponse.json();

    const existsMap = bitrixData.results;

    // Agora renderiza os cards com a informação de existência
    companiesList.forEach(company => {
      const existsInBitrix = existsMap[company.cnpj] || false;
      const card = document.createElement('div');
      card.className = 'company-card';
      card.innerHTML = `
        <div class="company-header">
          <div class="company-info">
            <h3 class="company-name">${company.razaoSocial}</h3>
            <p class="company-cnpj">${formatCNPJ(company.cnpj)}</p>
          </div>
          <div class="company-actions">
            <button class="action-btn expand-btn">
              <i class="fas fa-chevron-down"></i>
              Detalhes
            </button>
            <button class="action-btn bitrix-btn" ${existsInBitrix ? 'disabled title="Esta empresa já existe no Bitrix"' : ''} data-company-id="${company.id}">
              ${existsInBitrix ? '<i class="fas fa-ban"></i>' : '<i class="fas fa-paper-plane"></i>'}
              Enviar para Bitrix
            </button>
          </div>
        </div>
        ${existsInBitrix ? '<div class="bitrix-badge"><i class="fas fa-exclamation-circle"></i> Já existe no Bitrix</div>' : ''}
        <div class="company-details">
          <div class="detail-item">
            <span class="detail-label">Nome Fantasia</span>
            <span class="detail-value">${company.nomeFantasia || 'Não informado'}</span>
          </div>
          ${company.telefone1 ? `
          <div class="detail-item">
            <span class="detail-label">Telefone Principal</span>
            <span class="detail-value">${company.telefone1}</span>
          </div>
          ` : ''}
          ${company.telefone2 ? `
          <div class="detail-item">
            <span class="detail-label">Telefone Secundário</span>
            <span class="detail-value">${company.telefone2}</span>
          </div>
          ` : ''}
          ${company.email ? `
          <div class="detail-item">
            <span class="detail-label">Email</span>
            <span class="detail-value">${company.email}</span>
          </div>
          ` : ''}
          ${company.capitalSocial ? `
          <div class="detail-item">
            <span class="detail-label">Capital Social</span>
            <span class="detail-value">${company.capitalSocial}</span>
          </div>
          ` : ''}
          ${company.socios && company.socios.length > 0 ? `
          <div class="detail-item">
            <span class="detail-label">Sócios</span>
            <span class="detail-value">
              ${company.socios.join('<br>')}
            </span>
          </div>
          ` : ''}
          <div class="detail-item">
            <span class="detail-label">Endereço</span>
            <span class="detail-value">
              ${company.address}<br>
              ${company.neighborhood}, ${company.city} - ${company.state}
            </span>
          </div>
        </div>
      `;

      // Add event listeners for expand button
      const expandBtn = card.querySelector('.expand-btn');
      const details = card.querySelector('.company-details');
      expandBtn.addEventListener('click', () => {
        expandBtn.classList.toggle('expanded');
        details.classList.toggle('expanded');
        const icon = expandBtn.querySelector('i');
        icon.classList.toggle('fa-chevron-down');
        icon.classList.toggle('fa-chevron-up');
      });

      // Add event listener for Bitrix button
      const bitrixBtn = card.querySelector('.bitrix-btn');
      bitrixBtn.addEventListener('click', async () => {
        try {
          // Tratar o valor do capital social
          let capitalSocial = company.capitalSocial || '0';
          // Remove R$ e espaços
          capitalSocial = capitalSocial.replace('R$', '').trim();
          // Remove pontos de milhar
          capitalSocial = capitalSocial.replace(/\./g, '');
          // Substitui vírgula por ponto
          capitalSocial = capitalSocial.replace(',', '.');
          // Converte para número e volta para string
          capitalSocial = parseFloat(capitalSocial).toString();

          const companyData = {
            fantasy_name: company.nomeFantasia,
            company_name: company.razaoSocial,
            cnpj: company.cnpj,
            phone1: company.telefone1 || '',
            phone2: company.telefone2 || '',
            email: company.email || '',
            address: company.address || '',
            partners: company.socios ? company.socios.join(', ') : '',
            capitalSocial: capitalSocial,
            group: userData.group
          };

          await sendToBitrix(companyData);
        } catch (error) {
          showNotification('Erro ao enviar para o Bitrix: ' + error.message, 'error');
        }
      });

      container.appendChild(card);
    });
  } catch (error) {
    console.error('Error rendering companies:', error);
    showNotification('Erro ao renderizar as empresas: ' + error.message, 'error');
  }
}

// Função para enviar para o Bitrix
async function sendToBitrix(companyData) {
  // Em vez de enviar diretamente, mostra o modal de qualificação
  showQualificationModal(companyData);
}

function handleError(error) {
    console.error('Erro:', error);
    showNotification('Erro ao carregar os dados. Por favor, tente novamente.', 'error');
}
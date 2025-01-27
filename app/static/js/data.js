// User data with default values
export let userData = {
  name: '',
  company: '',
  group: '',
  initials: ''
};

// Function to fetch user data from server
export async function fetchUserData() {
  try {
    const response = await fetch('/api/current-user');
    if (!response.ok) {
      throw new Error('Failed to fetch user data');
    }
    const data = await response.json();

    // Update userData object
    userData.name = data.name || '';
    userData.company = data.company || '';
    userData.group = data.group || '';
    userData.initials = data.name ? data.name.charAt(0) : '';

    return userData;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}

export async function fetchCompanies(page = 1, searchTerm = '', filters = {}, typeQuery) {
  try {
    // Pega os valores dos filtros
    const queryParams = new URLSearchParams({
      page: page.toString(),
      search: searchTerm,
      city: filters.city || '',
      state: filters.state || '',
      neighborhood: filters.neighborhood || '',
      typeQuery // Adiciona o parâmetro typeQuery
    });
    console.log(queryParams.toString());

    const response = await fetch(`/api/companies?${queryParams}`);
    if (!response.ok) {
      throw new Error('Failed to fetch companies');
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching companies:', error);
    throw error;
  }
}

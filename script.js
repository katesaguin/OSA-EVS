// script.js

document.querySelector('.toggle-sidebar').addEventListener('click', () => {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
  
    if (sidebar.classList.contains('hidden')) {
      sidebar.classList.remove('hidden');
      mainContent.classList.remove('hidden');
    } else {
      sidebar.classList.add('hidden');
      mainContent.classList.add('hidden');
    }
  });
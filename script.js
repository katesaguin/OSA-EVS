function toggleSidebar() {
  const sidebar = document.querySelector('.sidebar');
  const mainContent = document.querySelector('.main-content');

  sidebar.classList.toggle('show');

  if (sidebar.classList.contains('show')) {
      mainContent.style.marginLeft = '250px';
  } else {
      mainContent.style.marginLeft = '0';
  }
}

// Add event listeners to sidebar links
document.querySelectorAll('.sidebar a').forEach(link => {
  link.addEventListener('click', function () {
      // Remove the 'active' class from all links
      document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));

      // Add the 'active' class to the clicked link
      this.classList.add('active');
  });
});
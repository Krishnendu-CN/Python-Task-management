// Optional global JS for future enhancements
document.addEventListener('htmx:responseError', (e) => {
  alert('An error occurred while processing your request.');
});
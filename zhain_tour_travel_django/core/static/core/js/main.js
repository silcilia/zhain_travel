const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav-links');
if (toggle) toggle.addEventListener('click', () => nav.classList.toggle('open'));

document.querySelectorAll('.nav-links a').forEach(link => {
  link.addEventListener('click', () => nav.classList.remove('open'));
});

document.querySelectorAll('[data-package]').forEach(link => {
  link.addEventListener('click', () => {
    const select = document.querySelector('select[name="package_id"]');
    if (select && link.dataset.packageId) {
      select.value = link.dataset.packageId;
    }
  });
});

setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => el.style.display = 'none');
}, 5000);

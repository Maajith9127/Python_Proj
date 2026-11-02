document.addEventListener('DOMContentLoaded', () => {
  // 1. Saaspo // Pages Filter Pills for the 6 Browser Showcase Cards
  const filterPills = document.querySelectorAll('[data-gallery-filter]');
  const galleryCards = document.querySelectorAll('.browser-card[data-category]');

  filterPills.forEach((pill) => {
    pill.addEventListener('click', () => {
      const cat = pill.getAttribute('data-gallery-filter');
      filterPills.forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');

      galleryCards.forEach((card) => {
        const cardCats = card.getAttribute('data-category') || '';
        if (cat === 'all' || cardCats.includes(cat)) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // 2. Hero Search Bar — Quick Filter / Jump across the 10 Writeup Sections
  const searchInput = document.getElementById('writeup-quick-search');
  const writeupCards = document.querySelectorAll('.writeup-BrowserCard');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      writeupCards.forEach((card) => {
        if (!q || card.innerText.toLowerCase().includes(q)) {
          card.style.display = 'block';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // 3. Python Code Workbench Tabs & Copy Button
  const codeTabs = document.querySelectorAll('.code-pill-tab');
  const codePanes = document.querySelectorAll('.code-pane');

  codeTabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-pane');
      codeTabs.forEach((t) => t.classList.remove('active'));
      codePanes.forEach((p) => p.classList.remove('active'));
      tab.classList.add('active');
      const el = document.getElementById(target);
      if (el) el.classList.add('active');
    });
  });

  const copyCodeBtn = document.getElementById('copy-code-btn');
  if (copyCodeBtn) {
    copyCodeBtn.addEventListener('click', () => {
      const activePre = document.querySelector('.code-pane.active pre');
      if (!activePre) return;
      navigator.clipboard.writeText(activePre.innerText).then(() => {
        const orig = copyCodeBtn.textContent;
        copyCodeBtn.textContent = 'Copied ✓';
        setTimeout(() => {
          copyCodeBtn.textContent = orig;
        }, 1600);
      });
    });
  }

  // 4. Scroll-Spy for the 10 Write-Up Sections Sidebar
  const sidebarLinks = document.querySelectorAll('.sidebar-nav-link');
  const sectionEls = document.querySelectorAll('.writeup-BrowserCard[id]');

  window.addEventListener(
    'scroll',
    () => {
      const pos = window.scrollY + 160;
      let current = '';
      sectionEls.forEach((sec) => {
        if (pos >= sec.offsetTop) {
          current = sec.getAttribute('id');
        }
      });
      if (current) {
        sidebarLinks.forEach((link) => {
          link.classList.toggle('active', link.getAttribute('href') === `#${current}`);
        });
      }
    },
    { passive: true }
  );
});

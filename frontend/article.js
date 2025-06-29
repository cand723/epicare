const listContainer = document.getElementById("article-list");
const searchInput = document.getElementById("search");
const themeBtn = document.getElementById("toggle-theme");

let allArticles = [];

async function fetchArticles() {
  const res = await fetch("/api/articles");
  allArticles = await res.json();
  renderArticles(allArticles);
}

function renderArticles(filteredArticles) {
  listContainer.innerHTML = "";
  filteredArticles.forEach((article) => {
    listContainer.innerHTML += `
      <div class="bg-white rounded-2xl shadow-md p-5 hover:shadow-lg transition duration-300">
        <h2 class="text-xl font-semibold mb-2 text-green-800">${article.title}</h2>
        <p class="text-sm text-gray-700 mb-4">${article.description}</p>
        <a href="article-detail.html?id=${article.id}" class="inline-block bg-green-600 text-white px-4 py-2 rounded-xl hover:bg-green-700 text-sm">Baca Selengkapnya</a>
      </div>
    `;
  });
}

searchInput.addEventListener("input", () => {
  const keyword = searchInput.value.toLowerCase();
  const filtered = allArticles.filter(
    (article) =>
      article.title.toLowerCase().includes(keyword) ||
      article.description.toLowerCase().includes(keyword)
  );
  renderArticles(filtered);
});

themeBtn.addEventListener("click", () => {
  document.body.classList.toggle("bg-green-50");
  document.body.classList.toggle("bg-gray-900");
  document.body.classList.toggle("text-white");
});

fetchArticles();

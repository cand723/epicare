document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const articleId = urlParams.get("id");

  const titleEl = document.getElementById("article-title");
  const metaEl = document.getElementById("article-meta");
  const imageEl = document.getElementById("article-image");
  const contentEl = document.getElementById("article-content");

  if (!titleEl || !metaEl || !imageEl || !contentEl) {
    console.error("Elemen artikel tidak ditemukan di halaman.");
    return;
  }

  if (!articleId) {
    titleEl.textContent = "Artikel tidak ditemukan";
    return;
  }

  fetch(`https://epicare-fullstack.onrender.com/api/articles/${articleId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error("Artikel tidak ditemukan");
      }
      return response.json();
    })
    .then(article => {
      // Judul
      titleEl.textContent = article.title || "Tanpa Judul";

      // Metadata
      const date = article.published_at
        ? new Date(article.published_at).toLocaleDateString("id-ID")
        : "Tanggal tidak tersedia";

      const author = article.author || "Penulis tidak diketahui";
      metaEl.textContent = `Oleh ${author} | Dipublikasikan pada ${date}`;

      // Gambar
      if (article.url_to_image) {
        imageEl.src = article.url_to_image;
        imageEl.alt = article.title || "Gambar artikel";
        imageEl.classList.remove("hidden");
      } else {
        imageEl.classList.add("hidden");
      }

      // Konten (dari markdown → HTML)
      if (article.content) {
        const html = marked.parse(article.content); // konversi markdown ke HTML
        contentEl.innerHTML = html;
      } else {
        contentEl.textContent = "Konten artikel tidak tersedia.";
      }

      // Sumber artikel
      const urlLinkEl = document.getElementById("article-url");
      const urlTextEl = document.getElementById("article-url-text");

      if (article.url) {
        urlLinkEl.href = article.url;
        urlTextEl.textContent = "Kunjungi artikel asli";
      } else {
        urlLinkEl.href = "#";
        urlTextEl.textContent = "Tautan tidak tersedia";
      }

    })
    .catch(error => {
      console.error(error);
      titleEl.textContent = error.message || "Gagal memuat artikel.";
      metaEl.textContent = "";
      contentEl.textContent = "";
      imageEl.classList.add("hidden");
    });
});

describe("Artikel User", () => {
  beforeEach(() => {
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".text-left > .w-full")
      .should("be.visible")
      .type("sanju329121@gmail.com");
    cy.get("#passwordInput").should("be.visible").type("sanju329121@gmail.com");
    cy.get("#loginButton").click().wait(1000);
    cy.get(":nth-child(1) > .px-3").click().wait(500);
  });

  // Positive Case
  it("Menampilkan Judul dan Deskripsi Halaman Artikel", () => {
    cy.get(".text-5xl")
      .should("be.visible")
      .contains("Jelajahi Artikel Kesehatan");
    cy.get(".text-center.mb-16 > .text-xl")
      .should("be.visible")
      .contains(
        "Dapatkan wawasan terpercaya dan terkini seputar kesehatan pernapasan dari para ahli, disajikan dengan gaya yang mudah dipahami."
      );
  });

  it("Menjalankan Fitur Search", () => {
    const searchText = "TBC";
    cy.get("#search").type(searchText);
    cy.window().then((win) => {
      cy.stub(win, "alert").as("alert");
    });
    cy.get(
      '[href="./article-detail.html?id=775cb6b8-768a-4efd-b931-4775ae2b009a"]'
    )
      .should("be.exist")
      .contains(`${searchText}`);
  });

  it("Navigasi Sidebar ke Halaman Artikel", () => {
    cy.get(
      '#popular-articles-list > [href="./article-detail.html?id=7afb6767-8757-4e4d-8997-d2b764789a64"]'
    ).click();
  });

  it("Navigasi ke Halaman Lain dari Sidebar", () => {
    cy.get(
      '#popular-articles-list > [href="./article-detail.html?id=7afb6767-8757-4e4d-8997-d2b764789a64"]'
    ).click();
    cy.get(
      '[href="./article-detail.html?id=e050f125-dbce-445b-8bc6-078351e5d986"]'
    ).click();
  });

  // Negative Case
  it("Menjalankan Fitur Search Tidak Ada Artikel", () => {
    cy.get("#search").type("testingnomatching");
    cy.get("#articles-container > .text-center")
      .should("be.visible")
      .contains("Tidak ada artikel yang ditemukan.");
  });
});

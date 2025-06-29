describe("Chat Bot", () => {
  beforeEach(() => {
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".text-left > .w-full")
      .should("be.visible")
      .type("sanju329121@gmail.com");
    cy.get("#passwordInput").should("be.visible").type("sanju329121@gmail.com");
    cy.get("#loginButton").click();
    cy.get(":nth-child(4) > .px-3").click();
    cy.contains("Chatbot Epicare");
  });

  // Positive Case
  it("Menampilkan Judul dan Deskripsi Halaman Chat Bot", () => {
    cy.get("#chat-input").should("be.visible");
    cy.get("#send-button").should("be.visible");
  });

  it("Melakukan Pengiriman Pesan ke Chat Bot", () => {
    const userMessage = "Apa itu TBC?";
    cy.get("#chat-input").type(userMessage);
    cy.get("#send-button").click().wait(7000);
    cy.get("#chat-scroll-container").contains(userMessage).should("exist");
    cy.get(":nth-child(3) > .max-w-\\[70\\%\\]").should("exist");
  });

  it("Menampilkan dan Menyembunyikan Sidebar", () => {
    cy.get("#toggle-sidebar-btn").click();
    cy.get("#sidebar").should("have.class", "sidebar-hidden");

    cy.get("#show-sidebar-btn").click();
    cy.get("#sidebar").should("have.class", "sidebar-visible");
  });

  it("Membuat Chat Baru", () => {
    cy.get("#new-chat-btn").click();
    cy.get("#chat-scroll-container").should("exist");
  });

  it("Melakukan Edit Judul Chat dari History", () => {
    cy.get(":nth-child(1) > .text-yellow-400 > .fa-solid")
      .click()
      .wait(500)
      .type("{selectall}") // select all text
      .type("{backspace}")
      .wait(1000) // hapus semua
      .type("EDITTT", { delay: 50 })
      .wait(1000) // ketik teks baru
      .type("{enter}"); // tekan Enter
  });

  it("Melakukan Delete Chat dari History", () => {
    cy.get(":nth-child(2) > .text-red-500 > .fa-solid").click().wait(5000);
  });

  // Negative Case
  it("Tidak bisa memuat informasi selain topik sekitar TBC", () => {
    cy.get("#chat-input").type("Apa itu Himatif");
    cy.get("#send-button").click();
    cy.get(":nth-child(3) > .max-w-\\[70\\%\\]", { timeout: 10000 }).should(
      "exist"
    );
    cy.get(":nth-child(3) > .max-w-\\[70\\%\\] > .prose > p").contains("Maaf");
  });
});

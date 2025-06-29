describe("Login dan Register", () => {
  it("Login", () => {
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".text-left > .w-full")
      .should("be.visible")
      .type("sanju329121@gmail.com");
    cy.get("#passwordInput").should("be.visible").type("sanju329121@gmail.com");
    cy.get("#loginButton").click().wait(5000);
  });
  it("Register", () => {
    const uniqueEmail = `test${Date.now()}@example.com`;
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".mt-auto > .underline").should("be.visible").click();
    // Isi semua field form
    cy.get('input[name="name"]').type("TESTINGBRAY");
    cy.get('select[name="gender"]').select("Female");
    cy.get('input[name="date"]').type("2002-03-01");
    cy.get('input[name="email"]').type(uniqueEmail);
    cy.get('input[name="password"]').type("password123");
    cy.get('input[name="terms"]').check();

    // Mock endpoint untuk mencegah beneran ngirim request ke backend
    cy.intercept("POST", "http://localhost:8000/register", {
      statusCode: 200,
      body: { message: "Akun berhasil dibuat!" },
    }).as("registerRequest");

    // Submit form
    cy.get("form").submit();

    // Tunggu request register selesai
    cy.wait("@registerRequest");

    // Periksa popup muncul dan berisi pesan yang benar
    cy.get("#popupModal")
      .should("have.class", "opacity-100")
      .and("contain.text", "Akun berhasil dibuat");

    // Klik tombol OK pada popup
    cy.get("#popupOkBtn").click();

    // Pastikan diarahkan ke halaman login
    cy.url().should("include", "login.html");
  });
});

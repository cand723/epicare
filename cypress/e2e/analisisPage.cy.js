describe("Analisis Gejala", () => {
  beforeEach(() => {
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".text-left > .w-full")
      .should("be.visible")
      .type("sanju329121@gmail.com");
    cy.get("#passwordInput").should("be.visible").type("sanju329121@gmail.com");
    cy.get("#loginButton").click().wait(1000);
    cy.get(":nth-child(2) > .px-3").click().wait(500);
    cy.contains("Analisis Gejala TBC");
  });

  // Positive Case
  it("Menampilkan Judul dan Deskripsi Halaman Analisis Gejala", () => {
    cy.contains("h1", "Analisis Gejala TBC").should("be.visible");
    cy.contains("p", "Sistem deteksi dini TBC berbasis gejala").should(
      "be.visible"
    );
  });
  it("Melakukan Prediksi Analisis Gejala", () => {
    for (let i = 1; i <= 10; i++) {
      // Pilih opsi ketiga (value="2") untuk setiap pertanyaan
      cy.get(`input[name="q${i}"][value="2"]`).check({ force: true });
    }
    cy.get(".bg-green-600").click();
    cy.get('input[name="q11"][value="1"]').check({ force: true });
    cy.get('input[name="q12"][value="2"]').check({ force: true });
    cy.get('input[name="q13"][value="1"]').check({ force: true });
    cy.get('input[name="q14"][value="0"]').check({ force: true });
    cy.get('input[name="q15"][value="2"]').check({ force: true });

    // Isi berat dan tinggi
    cy.get("#berat").type("60");
    cy.get("#tinggi").type("170");

    // Klik tombol prediksi
    cy.get("#predict-btn").click();

    cy.get("#prediction-result", { timeout: 5000 }).should(
      "not.have.class",
      "hidden"
    );
  });

  it("Melakukan Reset Jawaban", () => {
    for (let i = 1; i <= 10; i++) {
      // Pilih opsi ketiga (value="2") untuk setiap pertanyaan
      cy.get(`input[name="q${i}"][value="2"]`).check({ force: true });
    }
    cy.get(".bg-green-600").click();
    cy.get(".bg-red-600").click();
  });

  // Negative Case
  it("Melanjutkan Halaman Form Tanpa Mengisi", () => {
    cy.get(".bg-green-600").click();
    cy.get("#popup")
      .should("be.visible")
      .contains("Mohon isi semua pertanyaan sebelum melanjutkan.");
  });
});

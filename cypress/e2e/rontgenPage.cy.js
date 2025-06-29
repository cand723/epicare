describe("Analisis Rontgen", () => {
  beforeEach(() => {
    cy.get(".px-6 > .inline-block").should("be.visible").click();
    cy.get(".text-left > .w-full")
      .should("be.visible")
      .type("sanju329121@gmail.com");
    cy.get("#passwordInput").should("be.visible").type("sanju329121@gmail.com");
    cy.get("#loginButton").click().wait(1000);
    cy.get(":nth-child(3) > .px-3").click().wait(500);
    cy.get(".text-4xl").contains("Analisis Rontgen Dada");
  });
  const pdfPath = "sample.pdf"; 
  const normalPath = "images/sample-xray-normal.png"; 
  const tbcPath = "images/sample-xray-tbc.png"; 

  // Positive Case
  it("Menampilkan Judul dan Deskripsi Halaman Rontgen", () => {
    cy.contains("Analisis Rontgen Dada").should("be.visible");
    cy.get("#drop-area").should("be.visible");
    cy.get("#fileInput").should("exist");
  });

  it("Melakukan Analisis Rontgen - TBC", () => {
    cy.get('input[type="file"]').selectFile(`cypress/fixtures/${tbcPath}`, {
      force: true,
    });

    cy.get("#image-preview-container").should("be.visible");
    cy.get("#image-preview")
      .should("have.attr", "src")
      .and("include", "data:image");
    cy.get("#predictButton").should("be.visible").click();
    cy.get("#main-diagnosis-text")
      .should("be.visible")
      .contains("Pasien menunjukkan tanda-tanda terinfeksi TBC.");
    cy.get("#confidence-value").should("be.visible").contains("91%");
  });

  it("Melakukan Analisis Rontgen - Normal", () => {
    cy.get('input[type="file"]').selectFile(`cypress/fixtures/${normalPath}`, {
      force: true,
    });

    cy.get("#image-preview-container").should("be.visible");
    cy.get("#image-preview")
      .should("have.attr", "src")
      .and("include", "data:image");
    cy.get("#predictButton").should("be.visible").click();
    cy.get("#main-diagnosis-text")
      .should("be.visible")
      .contains("Hasil normal, tidak terdeteksi TBC.");
    cy.get("#confidence-value").should("be.visible").contains("97%");
  });

  // Negative Case
  it("Melakukan Upload Analisis Rontgen selain Gambar", () => {
    cy.get('input[type="file"]').selectFile(`cypress/fixtures/${pdfPath}`, {
      force: true,
    });
    cy.get("#image-preview-container").should("not.be.visible");
  });
});

function shortenURL() {
  const url = document.getElementById("url").value;
  const alias = document.getElementById("alias").value;

  fetch("/shorten", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ url, alias }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        alert(data.error);
      } else {
        const shortURL = data.short_url; // ✅ Assign shortURL properly

        // Display the shortened URL
        document.getElementById(
          "result"
        ).innerHTML = `Shortened URL: <a href="${shortURL}" target="_blank">${shortURL}</a>`;

        // Automatically generate QR code for the shortened URL
        generateQR(shortURL); // ✅ Now shortURL is correctly assigned
      }
    })
    .catch((error) => console.error("Error:", error));
}

function generateQR(shortURL = null) {
  if (!shortURL) {
    shortURL = document.querySelector("#result a")?.href; // Get the shortened URL from UI
  }

  if (!shortURL) {
    alert("Please shorten a URL first!");
    return;
  }

  console.log("Sending QR Request with URL:", shortURL); // Debugging

  fetch("/generate_qr", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: shortURL }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("QR Response Data:", data); // Debugging response
      if (data.error) {
        alert(data.error);
      } else {
        const qrPopup = document.getElementById("qr-popup");
        const qrImage = document.getElementById("qr-image");
        
        qrImage.src = data.qr_code;
        qrPopup.classList.remove("hidden");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("Failed to generate QR code. Please try again.");
    });
}

function closePopup() {
  document.getElementById("qr-popup").classList.add("hidden");
}

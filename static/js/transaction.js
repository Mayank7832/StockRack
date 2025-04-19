function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }


function deleteRow(event,button) {
    console.log("Delete button clicked");
    const row = button.closest("tr");
    const transactionId =  row.querySelector(".portfolio-id").value;
  
    if (!confirm("Are you sure you want to delete this transaction?")) {
      return;
    }
  
    fetch(`/portfolio/delete-transaction/${transactionId}/`, {
     
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },

    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          row.remove();
          alert("Transaction deleted!");
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((err) => console.error("Delete failed:", err));
  }
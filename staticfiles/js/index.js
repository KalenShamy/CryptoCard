window.addEventListener('load', function() {
    document.querySelector("button#add").onclick = function() {
        document.querySelector(".popup#add").style.left = 0;
    }
    document.querySelector(".popup#add #back").onclick = function() {
        document.querySelector(".popup#add").style.left = "";
    }
/*
    document.getElementById("add-submit-c").onclick = function() {
        fetch("add/customer", {
            "method": "POST",
            "body": JSON.stringify({
                "card_number": document.getElementById("add-number").value,
            })
        })
        window.location.reload();
    }

    document.getElementById("add-submit-m").onclick = function() {
        fetch("add/merchant", {
            "method": "POST",
            "body": JSON.stringify({
                "account_number": document.getElementById("add-number").value,
            })
        })
        window.location.reload();
    }
        */
       document.getElementById("add-submit-m").onclick = function() {
        fetch("add/merchant", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify({
                account_number: document.getElementById("add-number").value,
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            window.location.reload();
        })
        .catch(error => console.error('Error:', error));
    }
});

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};




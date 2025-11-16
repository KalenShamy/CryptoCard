window.addEventListener('load', function() {
    document.querySelector("button#add").onclick = function() {
        document.querySelector(".popup#add").style.left = 0;
    }
    document.querySelector(".popup#add #back").onclick = function() {
        document.querySelector(".popup#add").style.left = "";
    }

    document.getElementById("add-submit-c").onclick = function() {
        fetch("add/customer", {
            "method": "POST",
            "body": JSON.stringify({
                "card_number": document.getElementById("add-number").value,
            })
        })
        window.location.reload();
    }
});

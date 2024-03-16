function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

function likeAction() {
    console.log("in likeAction function");
    var data = getData();
    var post_pk = data["post_pk"];
    console.log(post_pk);
    fetch(`post/${post_pk}/like`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
    }) 
    .then(response => {
        if (!response.ok) {
            throw new Error ("Get num_like was not ok");
        }
        return response.json();
    })
    .then(responseData => {
        var num_likes = responseData["num_likes"];
        update(num_likes);
    })
    .catch(error => {
        console.error("Error occurred during like fetch:", error);
    });
}

function update(num_likes) {
    const element = document.getElementById("numLikes");
    element.textContent = num_likes;
}

function getData() {
    const likeBtn = document.getElementById("like-btn");
    const post_pk = likeBtn.parentElement.id;
    var data = {
        "post_pk": post_pk,
    };
    return data;
}
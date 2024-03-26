function getCSRFToken() {
    return document.querySelector('input[name="csrfmiddlewaretoken"]').value;
}

function likeAction(post_pk, numLikesId) {
    fetch(`/social/post/${post_pk}/like/`, {
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
        update(num_likes, numLikesId);
    })
    .catch(error => {
        console.error("Error occurred during like fetch:", error);
    });
}

function update(num_likes, numLikesId) {
    const element = document.getElementById(numLikesId);
    if (element) {
        element.textContent = num_likes;
    } else {
        console.error("Element with ID", numLikesId, "not found");
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function followUnfollow(evt){
    const username = evt.target.parentNode.querySelector(".username");
    const csrftoken = getCookie('csrftoken');
    const url = window.location.href;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    evt.preventDefault();
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({username: username.value, action: 'follow-unfollow'})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        console.log(data);
        if (data.is_following){
            evt.target.innerHTML = 'Unfollow';
            evt.target.classList.add('unfollow-button');
        } else {
            evt.target.innerHTML = 'Follow';
            evt.target.classList.remove('unfollow-button');
        }
        })
}


function sendLike(obj) {
    const csrftoken = getCookie('csrftoken');

    var postID;
    const type = obj.querySelector('.type').value;
    if (type == 'comment') {
        var postID = obj.parentNode.parentNode.parentNode.parentNode.querySelector('.post-interactions .obj-id').value;
        var objID = obj.querySelector('.obj-id').value;
    }
    else if (type == 'post') {
        var postID = obj.querySelector('.obj-id').value;
        var objID = postID;
    }

    const url = '/post/' + postID;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({action: 'like-unlike', object: type, objID: objID})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        const likes = obj.parentNode.parentNode.querySelector('.likes-qty');
        likes.innerHTML = data.qty;
    })
}


function sendComment(postID, commentText) {
    const csrftoken = getCookie('csrftoken');
    const url = '/post/' + postID;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({action: 'new-comment', text: commentText})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        var commentSection = document.querySelector('.post-main-view-info-comments');
        var postDescription = document.querySelector('.post-main-view-info-comments .post-desc').cloneNode(true);
        commentSection.innerHTML = '';
        commentSection.appendChild(postDescription);
        for (var k in data.comments) {
            commentSection.appendChild(createCommentHTML(data.comments[k]));
        }
        likeButton();
    })
}


function postViewRequest(evt) {
    var targetElement = evt.target;
    while (!targetElement.classList.contains('post-overlay')) {
        targetElement = targetElement.parentNode;
    }
    const postAnchor = targetElement.parentNode;
    const url = postAnchor.getAttribute('href');
    evt.preventDefault();
    fetch(url, {
        method: 'GET',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
        },
    })
    .then((response) => {
        return response.text();
    })
    .then((html) => {
        const postDivOverlay = document.body;
        postDivOverlay.classList.add('stop-scrolling');
        postDivOverlay.insertAdjacentHTML('beforeend', html);
        postCloseButton();
        inputCommentButton();
        likeButton();

    })
}


function postViewButton(){
    const posts = document.querySelectorAll('.post-div');

    for (var i = 0; i < posts.length; i++) {
        posts[i].addEventListener('click', postViewRequest);
    }
}


function generateFollowButtons(){
    const buttons = document.querySelectorAll('.follow-button')
    if (buttons){
        buttons.forEach(function(btn){
            btn.addEventListener('click', followUnfollow, false);
        })
    }
}


function postCloseButton() {
    const button = document.querySelector('.post-close-button');
    button.addEventListener('click', function () {
        const postCard = document.querySelector('.background-cover');
        postCard.remove();
        document.body.classList.remove('stop-scrolling');
    })
}


function postDescriptionButton() {
    const moreButtons = document.querySelectorAll('.more-button > p');
    for (var i = 0; i < moreButtons.length; i++) {
        var descriptionText = moreButtons[i].parentNode.parentNode.querySelector('p');
        if (descriptionText.offsetHeight < descriptionText.scrollHeight) {
            moreButtons[i].addEventListener('click', function() {
                const postDescription = this.parentNode.parentNode;
                postDescription.style.maxHeight = 'fit-content';
                postDescription.querySelector('p').style.height = 'fit-content';
                this.style.display = 'none';
            });
        }
        else {
            moreButtons[i].style.display = 'none';
        }
    }
}


function inputCommentButton() {
    const commentInputs = document.querySelectorAll('.input-comment > textarea');
    for (var i = 0; i < commentInputs.length; i++) {
        commentInputs[i].addEventListener('input', function() {
            this.style.height = '';
            this.style.height = this.scrollHeight + 'px';
            
            if (this.value == '') {
                this.parentNode.querySelector('div').classList.add('hide-icon');
            }
            else {
                this.parentNode.querySelector('div').classList.remove('hide-icon');
            } 
            
        });
        commentInputs[i].parentNode.querySelector('div').addEventListener('click', function () {
            const postID = this.parentNode.parentNode.querySelector('.obj-id').value;
            const commentText = this.parentNode.querySelector('textarea').value;
            sendComment(postID, commentText);
            this.parentNode.querySelector('textarea').value = '';
            this.classList.add('hide-icon');

        });
    }

}


function likeButton() {
    const likeButtons = document.querySelectorAll('.post-like-button');
    for (var i = 0; i < likeButtons.length; i++) {
        const likeStatus = likeButtons[i].querySelector('.like-status').value;
        if (likeStatus == 'liked') {
            likeButtons[i].querySelector('.not-liked').classList.add('hide-icon');
            likeButtons[i].querySelector('span').classList.remove('hide-icon');
        }
        
        if (!likeButtons[i].hasEventListener) {
            likeButtons[i].hasEventListener = true;
            likeButtons[i].addEventListener('click', function() {
                if (this.querySelector('.like-status').value == 'liked') {
                    this.querySelector('.not-liked').classList.remove('hide-icon');
                    this.querySelector('span').classList.add('hide-icon');
                    this.querySelector('.like-status').value = 'not-liked';
                }
                else {
                    this.querySelector('.not-liked').classList.add('hide-icon');
                    this.querySelector('span').classList.remove('hide-icon');   
                    this.querySelector('.like-status').value = 'liked';
                }
                sendLike(this);
            });
        }
    }
}


function createCommentHTML(data) {
    const dateOptions = {day: 'numeric', month: 'long'};
    var template = document.getElementById('comment-template');
    var comment = template.content.cloneNode(true);

    var img = comment.querySelector('img');
    img.src = data.user_pic;
    img.alt = 'Foto de perfil de ' + data.username;

    var date = new Date(data.post_date)
    comment.querySelector('.comment-username p').innerHTML = data.username;
    comment.querySelector('.comment-main').innerHTML = data.text;
    comment.querySelector('.comment-date').innerHTML = date.toLocaleDateString('pt-BR', dateOptions);
    comment.querySelector('.likes-qty').innerHTML = data.likes_qty;

    comment.querySelector('.like-status').value = data.liked ? 'liked' : 'not-liked';
    comment.querySelector('.obj-id').value = data.id;

    if (data.liked) {
        comment.querySelector('.post-like-button > svg').classList.add('hide-icon');
    }
    else {
        comment.querySelector('.post-like-button > span').classList.add('hide-icon');
    }

    return comment;
}


if(window.addEventListener) {
    window.addEventListener('load',generateFollowButtons,false);
} else {
    window.attachEvent('onload',generateFollowButtons);
}


document.addEventListener('DOMContentLoaded', function() {
    postDescriptionButton();
    inputCommentButton();
    likeButton();
    postViewButton();

    
    
})
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
        } else {
            evt.target.innerHTML = 'Follow';
        }
        })
}


function generateFollowButtons(){
    const buttons = document.querySelectorAll('.follow-button')
    if (buttons){
        buttons.forEach(function(btn){
            btn.addEventListener('click', followUnfollow, false);
        })
    }
}

function sendLike(postID) {
    // TODO: implementar envio do like para o servidor
    console.log('Like enviado :)');
    console.log(postID);
}

function formatLikes(number) {
    // TODO: implementar formatação
    return number;
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
    }
}


function postLikeButton() {
    const likeButtons = document.querySelectorAll('.post-like-button');
    for (var i = 0; i < likeButtons.length; i++) {
        const likeStatus = likeButtons[i].querySelector('.like-status').value;
        if (likeStatus == 'liked') {
            likeButtons[i].querySelector('.not-liked').classList.add('hide-icon');
            likeButtons[i].querySelector('span').classList.remove('hide-icon');
        }
        likeButtons[i].addEventListener('click', function() {
            var likes = this.parentNode.parentNode.querySelector('.likes-qty');
            if (this.querySelector('.like-status').value == 'liked') {
                this.querySelector('.not-liked').classList.remove('hide-icon');
                this.querySelector('span').classList.add('hide-icon');
                this.querySelector('.like-status').value = 'not-liked';
                likes.innerHTML = formatLikes(parseInt(likes.innerHTML) - 1);
                
            }
            else {
                this.querySelector('.not-liked').classList.add('hide-icon');
                this.querySelector('span').classList.remove('hide-icon');   
                this.querySelector('.like-status').value = 'liked';
                likes.innerHTML = formatLikes(parseInt(likes.innerHTML) + 1);
            }
            sendLike(this.querySelector('.post-id').value)
        });
    }
}


if(window.addEventListener) {
    window.addEventListener('load',generateFollowButtons,false);
} else {
    window.attachEvent('onload',generateFollowButtons);
}

document.addEventListener('DOMContentLoaded', function() {
    postDescriptionButton();
    inputCommentButton();
    postLikeButton();

    
    
})
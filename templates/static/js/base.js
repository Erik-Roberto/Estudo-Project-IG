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
    console.log('Like enviado :)');
    console.log(postID);
}

function formatLikes(number) {
    return number;
}


if(window.addEventListener) {
    window.addEventListener('load',generateFollowButtons,false);
} else {
    window.attachEvent('onload',generateFollowButtons);
}

document.addEventListener('DOMContentLoaded', function() {
    const moreButtons = document.querySelectorAll('.more-button > p');
    for (var i = 0; i < moreButtons.length; i++) {
        moreButtons[i].addEventListener('click', function() {
            const postDescription = this.parentNode.parentNode;
            postDescription.style.maxHeight = 'fit-content';
            postDescription.querySelector('p').style.height = 'fit-content';
            this.style.display = 'none';

        });
    }

    const commentInputs = document.querySelectorAll('.input-comment > textarea');
    for (var i = 0; i < commentInputs.length; i++) {
        commentInputs[i].addEventListener('input', function() {
            this.style.height = '';
            this.style.height = this.scrollHeight + 'px';
            

            if (this.value == '') {
                const bgColor = getComputedStyle(document.documentElement)
                    .getPropertyValue('--bg-color');
                this.parentNode.querySelector('div')
                    .style.color = bgColor;
            }
            else {
                const textColor = getComputedStyle(document.documentElement)
                    .getPropertyValue('--text-blue');
                this.parentNode.querySelector('div')
                    .style.color = textColor;
            } 

        });
    }
    
    const likeButtons = document.querySelectorAll('.post-like-button');
    for (var i = 0; i < likeButtons.length; i++) {
        const likeStatus = likeButtons[i].parentNode.querySelector('.like-status').value;
        if (likeStatus == 'liked') {
            this.querySelector('.not-liked').classList.add('hide-icon');
            this.querySelector('span').classList.remove('hide-icon');
        }
        likeButtons[i].addEventListener('click', function() {
            var likes = this.parentNode.parentNode.querySelector('.likes-qty');
            // sendLike(this.querySelector('.post-id').value);
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

})
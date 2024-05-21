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


function getObjInfo(obj) {
    const type = obj.querySelector('.type').value;
    if (type == 'comment') {
        var postID = obj.parentNode.parentNode.parentNode.parentNode.querySelector('.post-interactions .obj-id').value;
        var objID = obj.querySelector('.obj-id').value;
        var url = '/post/' + objID + '/comments/' ;
    }
    else if (type == 'post') {
        var postID = obj.querySelector('.obj-id').value;
        var objID = postID;
        var url = '/post/' + objID + '/likes/' ;
    }
    return {
        postID: postID,
        objID: objID,
        type: type,
        url: url,
    }
}


function followUnfollow(evt){
    const username = evt.target.parentNode.querySelector('.username').value;
    const url = evt.target.parentNode.querySelector('.post-url').value;
    const csrftoken = getCookie('csrftoken');
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    evt.preventDefault();
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({
            target: username,
            action: 'follow-unfollow',
        })
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        updateFollowersAndFollowing(data, evt.target);
    })
}


function sendLike(obj) {
    const csrftoken = getCookie('csrftoken');

    var objInfo = getObjInfo(obj);

    const url = objInfo.url;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({objID: objInfo.objID})
    })
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
    const url = '/post/' + postID + '/';
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({text: commentText})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        var commentSection = document.querySelector('.post-main-view-info-comments');
        if (!commentSection) { // TODO: Melhorar lógica. Query não encontra objetos quando comentário é enviado da homepage
            console.log('Não achei comentários :(');
            return;
        }
        var postDescription = document.querySelector('.post-main-view-info-comments .post-desc').cloneNode(true);
        commentSection.innerHTML = '';
        commentSection.appendChild(postDescription);
        for (var k in data.comments) {
            commentSection.appendChild(createCommentHTML(data.comments[k]));
        }
        likeButton();
    })
}


function removeFollower(element, username) {
    const csrftoken = getCookie('csrftoken');
    const url = window.location.href;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({username: username.value, action: 'remove-follower'})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        element.remove();
        updateFollowersAndFollowing(data);
    })
}


function likesView(obj) {
    const csrftoken = getCookie('csrftoken');

    var objInfo = getObjInfo(obj);

    const url = objInfo.url;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    
    fetch(request, {
        method: 'GET',
        mode: 'same-origin',
    })
    .then((response) => {
        return response.text();
    })
    .then((html) => {
        document.body.classList.add('stop-scrolling');
        document.body.insertAdjacentHTML('beforeend', html);
        postCloseButton();
        createFollowButtons();
        createSearchEvent();
    })
}


function postViewRequest(url) {
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
        document.body.classList.add('stop-scrolling');
        document.body.insertAdjacentHTML('beforeend', html);
        postCloseButton();
        inputCommentButton();
        likeButton();
        createLikesViewButton();
    })
}


function relationshipViewRequest(url) {
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
        document.body.classList.add('stop-scrolling');
        document.body.insertAdjacentHTML('beforeend', html);
        postCloseButton();
        createFollowButtons();
        createRemoveFollowerButton();
        createSearchEvent();

    })
}


function getSearchedUsers(input) {
    const mainUrl = input.parentNode.querySelector('.search-url').value;
    const query = new URLSearchParams({q: input.value});
    const url = mainUrl + '?' + query.toString();
    fetch(url)
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        const userList = input.parentNode.parentNode.parentNode.querySelector('.users-list');
        userList.innerHTML = '';
        if (data.user_list) {
            for (var i = 0; i < data.user_list.length; i++) {
                userList.appendChild(createSearchedUserCards(
                    data.user_list[i],
                    data.profile_user,
                    data.show_bio,
                    data.show_relationship,
                    data.show_remove,
                ))
            }
        }
        createFollowButtons();
        createRemoveFollowerButton();
    })
}


function postViewButton(){
    const posts = document.querySelectorAll('.post-div');

    for (var i = 0; i < posts.length; i++) {
        posts[i].addEventListener('click', function (evt) {
            var targetElement = evt.target;
            while (!targetElement.classList.contains('post-overlay')) {
                targetElement = targetElement.parentNode;
            }
            const postAnchor = targetElement.parentNode;
            const url = postAnchor.getAttribute('href');
            evt.preventDefault();
            return postViewRequest(url);
        });
    }
}


function createLikesViewButton() {
    //FIXME: arrumar query para apenas os likes serem clicados
    const buttons = document.querySelectorAll('.info-data');

    for (var i = 0; i < buttons.length; i++) {
        if (!buttons[i].hasEventListener) {
            buttons[i].hasEventListener = true;
            buttons[i].addEventListener('click', function() {
                // FIXME: Arrumar maneira de diferenciar comment de post
                const obj = this.parentNode.parentNode.querySelector('.post-like-button');
                return likesView(obj);
            })
        }
    }
}


function createFollowButtons(){
    const buttons = document.querySelectorAll('.follow-button')
    if (buttons){
        for (var i = 0; i < buttons.length; i++) {
            if (!buttons[i].hasEventListener) {
                buttons[i].hasEventListener = true;
                buttons[i].addEventListener('click', function(evt){
                    return followUnfollow(evt);
                })
            }
        }
    }
}


function createRelationshipButtons() {
    const buttons = document.querySelectorAll('.relationship-button');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function() {
            const url = this.querySelector('input').value;
            return relationshipViewRequest(url);
        })
    }
}


function createRemoveFollowerButton() {
    const buttons = document.querySelectorAll('.remove-follower');
    for (var i = 0; i < buttons.length; i++) {
        if (!buttons[i].hasEventListener) {
            buttons[i].hasEventListener = true;
            buttons[i].addEventListener('click', function() {
                const username = this.parentNode.querySelector('.username');
                const userElement = this.parentNode.parentNode;
                return removeFollower(userElement, username);
            })
        }
    }

}


function createNavbarSearchButton(){ 
    const navbarButton = document.querySelector('#navbar-search');
    navbarButton.addEventListener('click', (evt) => {
        evt.preventDefault();
        evt.stopPropagation();
        const navbar = document.querySelector('.navbar');
        if (navbar.classList.contains('smallbar')) {
            navbar.classList.remove('smallbar');
            document.body.classList.remove('stop-scrolling');
        }
        else {
            navbar.classList.add('smallbar');
            document.body.classList.add('stop-scrolling');
        }
    })

    document.querySelector('.search-card').addEventListener('click', (evt) => {
        evt.stopPropagation();
    });

    document.addEventListener('click', () => {
        const navbar = document.querySelector('.navbar');
        if (navbar.classList.contains('smallbar')) {
            navbar.classList.remove('smallbar');
            document.body.classList.remove('stop-scrolling');
        }
    });
}


function createSearchEvent() {
    const searchInputs = document.querySelectorAll('.search-input');
    for (var i = 0; i < searchInputs.length; i++) {
        if (!searchInputs[i].hasEventListener) {
            searchInputs[i].hasEventListener = true;
            searchInputs[i].addEventListener('keyup', (evt) => {
                return getSearchedUsers(evt.target);
            })
        }
    }
}


function postCloseButton() {
    const bgCoverLayer = document.querySelectorAll('.background-cover');
    for (var i = 0; i < bgCoverLayer.length; i++) {
        if (!bgCoverLayer[i].layer) {
            document.layer += 1;
            bgCoverLayer[i].layer = document.layer;
            bgCoverLayer[i].setAttribute('id', 'bgc' + document.layer);

            const button = bgCoverLayer[i].querySelector('.overlay-close-button');

            button.addEventListener('click', function () {
                document.getElementById('bgc'+ document.layer).remove();
                document.layer -= 1;
                if (document.layer == 0) {
                    document.body.classList.remove('stop-scrolling');
                }
            })
        }

    }
    
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
    const commentButtonIcons = document.querySelectorAll('.post-comment');
    const commentInputs = document.querySelectorAll('.input-comment > textarea');

    
    for (var i = 0; i < commentButtonIcons.length; i++) {
        commentButtonIcons[i].addEventListener('click', function (){
            const commentInput = this.parentNode.parentNode.parentNode.querySelector('.input-comment > textarea');
            commentInput.focus();
        })
    }

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
        if (!commentInputs[i].hasEventListener){
            commentInputs[i].hasEventListener = true;
            commentInputs[i].parentNode.querySelector('div').addEventListener('click', function () {
                const commentText = this.parentNode.querySelector('textarea').value;
                var postID;
                if (document.layer == 0) {
                    postID = this.parentNode.parentNode.parentNode.querySelector('.obj-id').value;
                    const url = this.parentNode.parentNode.querySelector('.post-url').value;
                    postViewRequest(url);
                }
                else {
                    postID = this.parentNode.parentNode.querySelector('.obj-id').value;
                }
                sendComment(postID, commentText);
                this.parentNode.querySelector('textarea').value = '';
                this.classList.add('hide-icon');
                
            });
        }
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


function showCommentsButtons() {
    const buttons = document.querySelectorAll('.show-comments');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function () {
            const url = this.querySelector('.post-url').value;
            return postViewRequest(url);
        })
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


function updateFollowersAndFollowing(data, button = null) {
    
    if (button) {
        if (data.is_following){
            button.innerHTML = 'Seguindo';
            button.classList.add('unfollow-button');
        } else {
            button.innerHTML = 'Seguir';
            button.classList.remove('unfollow-button');
        }
    }

    const followersInfo = document.querySelector('.followers-url ~ p');
    const followingInfo = document.querySelector('.following-url ~ p');
    if (followersInfo && followingInfo) {
        followersInfo.innerHTML = data.followers + ' seguidores';
        followingInfo.innerHTML = data.following + ' seguindo';
    }
}


function createSearchedUserCards(data, profileUser = null, showBio = false, showRelationship = false, showRemove = false) {
    const template = document.getElementById('users-template');
    var userCard = template.content.cloneNode(true);

    const profilePicture = userCard.querySelector('img');
    profilePicture.src = data.user_pic;
    profilePicture.alt = 'Foto de perfil de ' + data.username;

    userCard.querySelector('a').href = data.profile_url;
    userCard.querySelector('a > p').innerHTML = data.username;
    if (showBio) {
        userCard.querySelector('.max-text').innerHTML = data.bio;
    }

    if (showRelationship) {
        userCard.querySelector('.username').value = data.username;
        
        if (profileUser) {
            userCard.querySelector('.post-url').value = '/' + profileUser + '/';
        }
        else {
            userCard.querySelector('.post-url').value = '/' + data.username + '/';
        }

        if (!data.is_following) {
            const btn = userCard.querySelector('.follow-button');
            btn.innerHTML = 'Seguir';
            btn.classList.remove('unfollow-button');
        }

        if (!showRemove) {
            userCard.querySelector('.remove-follower').remove();
        }
    }
    else {
        userCard.querySelector('.relationship-buttons').remove();
    }
    return userCard;
}

document.addEventListener('DOMContentLoaded', function() {
    postDescriptionButton();
    inputCommentButton();
    likeButton();
    postViewButton();
    showCommentsButtons();
    createRelationshipButtons();
    createFollowButtons();
    createRemoveFollowerButton();
    createLikesViewButton();
    createNavbarSearchButton();
    createSearchEvent();
    
    document.layer = 0;
    
})
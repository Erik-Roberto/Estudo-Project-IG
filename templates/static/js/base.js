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
    const buttonId = evt.target.id;
    const csrftoken = getCookie('csrftoken');
    const url = window.location.href;
    const request = new Request(
        url,
        {headers: {'X-CSRFToken': csrftoken}}
    )
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({button: buttonId, action: 'follow-unfollow'})
    }
    )
    .then((response) => {
        return response.json();
    })
    .then((data) => {
        const buttonId = 'button-' + String(data.id);
        if (data.is_following){
            setValue(buttonId, 'Unfollow');
        } else {
            setValue(buttonId, 'Follow');
        }
        })
}


function setValue(id, newValue){
    const element = document.getElementById(id);
    element.innerHTML = newValue;
}


function generateFollowButtons(){
    const buttons = document.querySelectorAll('.follow-button')
    if (buttons){
        buttons.forEach(function(btn){
            btn.addEventListener('click', followUnfollow, false);
        })
    }
}


if(window.addEventListener) {
    window.addEventListener('load',generateFollowButtons,false);
} else {
    window.attachEvent('onload',generateFollowButtons);
}

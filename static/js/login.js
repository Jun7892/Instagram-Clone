const idInput = document.getElementById('userid');
const pwInput = document.getElementById('userpw');
const loginInput = document.getElementsByClassName('container')[0];
const loginBtn = document.getElementById('btn_login');
// const linkToMain = document.getElementsByTagName('a')[0];

function idCheck() {
    return pwInput.value.length >= 3 ? true : false;
}
function pwCheck() {
    return pwInput.value.length >= 3 ? true : false;
}

loginInput.addEventListener('keyup', function(event) {
    const completedInput = (idCheck() && pwCheck());
    loginBtn.disabled = completedInput ? false : true;
})


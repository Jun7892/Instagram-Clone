const idInput = document.getElementById('userid');
const pwInput = document.getElementById('userpw');
const loginInput = document.getElementsByClassName('container')[0];
const loginBtn = document.getElementById('btn_login');
const linkToMain = document.getElementsByTagName('a')[0];

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

// 게시 버튼 활성화 (예정)
// const coBtn = document.getElementById('submit-comment2');
// const coInput = document.getElementById('input-comment2');

// function commentCheck() {
//     return coInput.value.length >= 2 ? true : false;
// }
// loginInput.addEventListener('keyup', function(event) {
//     const completedInput = commentCheck();
//     coBtn.disabled = completedInput ? false : true;
// })



function login() {
    $.ajax({
        type: "POST",
        url: "/api/login",
        data: { id_give: $('#userid').val(), pw_give: $('#userpw').val() },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token']);
                alert('로그인 완료!')
                window.location.href = '/'
            } else {
                alert(response['msg'])
            }
        }
    })
}



// 댓글을 한 글자라도 달아야 disabled된 게시 버튼이 active됨.
const coInput = document.getElementById('input-comment2');
const commInput = document.getElementsByClassName('comment')[1];
const coBtn = document.getElementById('submit-comment2');

function coCheck() {
    return coInput.value.length >= 1 ? true : false;
}

commInput.addEventListener('keyup', function(event) {
    const completedInput = (coCheck());
    coBtn.disabled = completedInput ? false : true;
})

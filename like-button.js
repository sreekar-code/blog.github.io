document.addEventListener('DOMContentLoaded', function() {
  const likeButton = document.getElementById('likeButton');
  const likeCount = likeButton.querySelector('.like-count');
  let count = parseInt(localStorage.getItem('likeCount')) || 0;

  updateLikeCount();

  likeButton.addEventListener('click', function() {
    if (!likeButton.classList.contains('liked')) {
      count++;
      likeButton.classList.add('liked');
    } else {
      count--;
      likeButton.classList.remove('liked');
    }
    localStorage.setItem('likeCount', count);
    updateLikeCount();
  });

  function updateLikeCount() {
    likeCount.textContent = count;
  }
});

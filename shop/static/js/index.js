
  function likePost(postId) {
    const likeButton = document.getElementById(`like-btn-${postId}`);
    fetch(`/like/${postId}`, { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        if (data.liked) {
          
          likeButton.innerHTML = '<i class="fa-solid fa-thumbs-up fa-lg"></i>';
        } else {
          
          likeButton.innerHTML = '<i class="fa-regular fa-thumbs-up fa-lg"></i>';
        }
      })
      .catch(error => console.error('Error:', error));
  }



  
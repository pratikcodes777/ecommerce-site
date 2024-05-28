
  function likePost(postId) {
    const likeCount = document.getElementById(`like-count-${postId}`);
    const likeButton = document.getElementById(`like-btn-${postId}`);
    fetch(`/like/${postId}`, { method: 'POST' })
      .then(response => response.json())
      .then(data => {
        if (data.liked) {
          
          likeButton.innerHTML = '<i class="fa-solid fa-thumbs-up fa-lg"></i>';
        } else {
          
          likeButton.innerHTML = '<i class="fa-regular fa-thumbs-up fa-lg"></i>';
        }
        likeCount.innerHTML = data.like_count;
      })
      .catch(error => console.error('Error:', error));
  }


  
  document.querySelectorAll('.plus-cart').forEach(button => {
    button.addEventListener('click', function() {
        console.log('Button clicked');
        
        const id = this.getAttribute('pid').toString();
        const quantity = this.parentNode.children[2];
        
        fetch(`/pluscart?cart_id=${id}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            quantity.innerText = data.quantity;
            document.getElementById(`quantity${id}`).innerText = data.quantity;
            document.getElementById('amount_tt').innerText = data.amount;
            document.getElementById('totalamount').innerText = data.total;
        })
        .catch(error => console.error('Error:', error));
    });
});

  
document.querySelectorAll('.minus-cart').forEach(button => {
  button.addEventListener('click', function() {
      console.log('Button clicked');

      const id = this.getAttribute('pid').toString();
      const quantityElement = this.parentNode.children[2];
      const currentQuantity = parseInt(quantityElement.innerText);

      if (currentQuantity <= 1) {
          console.log('Quantity cannot be less than 1');
          return;
      }

      fetch(`/minuscart?cart_id=${id}`, {
          method: 'GET'
      })
      .then(response => response.json())
      .then(data => {
          console.log(data);
          quantityElement.innerText = data.quantity;
          document.getElementById(`quantity${id}`).innerText = data.quantity;
          document.getElementById('amount_tt').innerText = data.amount;
          document.getElementById('totalamount').innerText = data.total;
      })
      .catch(error => console.error('Error:', error));
  });
});



// $('.remove-cart').click(function(){
    
//     var id = $(this).attr('pid').toString()

//     var to_remove = this.parentNode.parentNode.parentNode.parentNode

//     $.ajax({
//         type: 'GET',
//         url: '/removecart',
//         data: {
//             cart_id: id
//         },

//         success: function(data){
//             document.getElementById('amount_tt').innerText = data.amount
//             document.getElementById('totalamount').innerText = data.total
//             to_remove.remove()
//         }
//     })


// })


document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('[id^="rating-stars-"]').forEach(starContainer => {
      const productId = starContainer.id.split('-')[2];
      const ratingValue = parseFloat(document.getElementById(`rating-value-${productId}`).innerText);
      updateRatingStars(productId, ratingValue);
  });
});

function rateProduct(productId, ratingValue) {
  fetch(`/rate_product/${productId}/${ratingValue}`, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          const newRating = parseFloat(data.new_rating).toFixed(1); 
          document.getElementById(`rating-value-${productId}`).innerText = newRating;
          updateRatingStars(productId, newRating);
      } else {
          alert(data.message);
      }
  })
  .catch(error => console.error('Error:', error));
}

function updateRatingStars(productId, newRating) {
  const stars = document.querySelectorAll(`#rating-stars-${productId} .star`);
  const wholeStars = Math.floor(newRating);
  const fraction = newRating - wholeStars;
  const hasHalfStar = fraction >= 0.25 && fraction < 0.75;

  stars.forEach((star, index) => {
      if (index < wholeStars) {
          star.innerHTML = '<i class="fa fa-star text-primary"></i>';
      } else if (index === wholeStars && hasHalfStar) {
          star.innerHTML = '<i class="fa fa-star-half-alt text-primary"></i>';
      } else if (index === wholeStars && !hasHalfStar && fraction >= 0.75) {
          star.innerHTML = '<i class="fa fa-star text-primary"></i>';
      } else {
          star.innerHTML = '<i class="fa fa-star text-muted"></i>';
      }
  });
}

// CSRF helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {

    // Update the buttons for a card based on quantity
    function updateButton(card, qty) {
        const cartAction = card.find('.cart-action');
        cartAction.empty();
        if (qty > 0) {
            cartAction.append(
                `<div class="d-flex align-items-center gap-1">
                    <button class="btn btn-sm btn-outline-danger decrease-btn">-</button>
                    <span class="quantity">${qty}</span>
                    <button class="btn btn-sm btn-outline-success increase-btn">+</button>
                    <a href="/orders/cart/" class="btn btn-sm btn-primary">Go to Cart</a>
                </div>
            `);
        } else {
            cartAction.append(`<button class="add-cart-btn btn btn-success btn-sm">🛒 Add</button>`);
        }
    }

    // Load cart from server on page load
    function loadCart() {
        $.ajax({
            url: '/orders/get_cart/',
            type: 'GET',
            success: function(response) {
                response.items.forEach(item => {
                    const card = $(`.food-card[data-food-id="${item.food_id}"]`);
                    updateButton(card, item.quantity);
                });
            }
        });
    }

    loadCart();

    // Add to Cart button click
    $(document).on('click', '.add-cart-btn', function () {
    const card = $(this).closest('.food-card');
    const foodId = card.data('food-id');

    $.ajax({
        url: `/orders/add/${foodId}/`,   // ye sahi hona chahiye
        type: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')},  // CSRF must
        success: function(response) {
            if(response.status === "success"){
                updateButton(card, response.quantity);
            } else if(response.status === "login_required"){
                alert('Please login first!');
            }
        },
        error: function() {
            alert('Something went wrong! Try again.');
        }
    });
});

    // Increase quantity
    $(document).on('click', '.increase-btn', function () {
        const card = $(this).closest('.food-card');
        const foodId = card.data('food-id');

        $.ajax({
            url: `/orders/update/${foodId}/increase/`,
            type: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function(response) {
                updateButton(card, response.quantity);
            }
        });
    });

    // Decrease quantity
    $(document).on('click', '.decrease-btn', function () {
        const card = $(this).closest('.food-card');
        const foodId = card.data('food-id');

        $.ajax({
            url: `/orders/update/${foodId}/decrease/`,
            type: 'POST',
            headers: {'X-CSRFToken': getCookie('csrftoken')},
            success: function(response) {
                updateButton(card, response.quantity);
            }
        });
    });

});


$(document).ready(function () {
    // Append the cart button and popup container to the body
    $('body').append(`
        <div id="cart-popup-container">
            <button id="cart-button" class="btn btn-warning" style="border-radius: 20px 0 0 20px">🛒 Cart</button>
            <div id="cart-popup" class="card shadow">
                <div class="card-body">
                    <h5 class="card-title">Cart Contents</h5>
                    <div id="cart-items">
                        <p>Loading...</p>
                    </div>
                    <a href="/cart/" class="btn btn-dark">Go to Cart</a>
                </div>
            </div>
        </div>
    `);


    $('#cart-button').on('click', function () {
        $('#cart-popup').toggle();
    });

    function updateCartPopup() {
        $.get('/fetch_cart/', function (data) {
            const cartItems = data.cart_items;
            const total = data.total;
            let cartHtml = '';

            if (cartItems.length === 0) {
                cartHtml = '<p>Your cart is empty.</p>';
            } else {
                cartItems.forEach(function (item) {
                    cartHtml += `
                        <div class="cart-item">
                            <p><strong>${item.name}</strong> - $${item.price} x ${item.quantity} = $${item.total_price}</p>
                        </div>
                    `;
                });
                cartHtml += `<hr><p><strong>Total:</strong> $${total}</p>`;
            }
            $('#cart-items').html(cartHtml);
        });
    }
    updateCartPopup();
});

// ===================== GLOBAL VARIABLES =====================
let qty = 1;
const overlay = $('.sheet-overlay');
const variantSheet = $('#variant-bottom-sheet');

// Append Repeat Customization Sheet
const repeatSheetHTML = `
<div id="repeat-customization-sheet" class="variant-sheet" style="display:none;">
    <div class="sheet-header">
        <div class="sheet-title">
            <img class="sheet-image" src="" alt="Food Image">
            <div class="sheet-name">Food Name</div>
        </div>
        <button id="repeat-sheet-close">&times;</button>
    </div>
    <div class="sheet-body">
        <div class="repeat-last">
            <h5>Repeat last used customization?</h5>
            <div class="last-variant"></div>
        </div>
        <div class="add-new-variant mt-3">
            <button class="btn btn-outline-primary" id="add-new-customization">+ Add new customization</button>
        </div>
    </div>
</div>
`;
$('body').append(repeatSheetHTML);
const repeatSheet = $('#repeat-customization-sheet');

// ===================== HELPER FUNCTIONS =====================
function updateCardUI(foodId) {
    const card = $(`.food-card[data-food-id="${foodId}"]`);
    const addBtn = card.find('.add-cart-btn');
    let qtyBox = card.find('.qty-box');

    let totalQty = 0;
    if (cartItems[foodId]) {
        totalQty = Object.values(cartItems[foodId].variants)
            .reduce((sum, v) => sum + v.qty, 0);
    }

    if (totalQty > 0) {
        addBtn.hide();
        if (qtyBox.length === 0) {
            card.find('.card-add-area').append(`
                <div class="qty-box">
                    <button type="button" class="minus-btn btn btn-sm btn-outline-dark">-</button>
                    <span class="card-qty">${totalQty}</span>
                    <button type="button" class="plus-btn btn btn-sm btn-outline-dark">+</button>
                </div>
            `);
        } else {
            qtyBox.removeClass('d-none');
            qtyBox.find('.card-qty').text(totalQty);
        }
    } else {
        if (qtyBox.length > 0) qtyBox.addClass('d-none');
        addBtn.show();
    }
}

// ===================== OPEN VARIANT SHEET =====================
function openVariantSheet(foodId) {
    $.get(`/orders/variants/${foodId}/`, function (data) {
        variantSheet.find('.sheet-name').text(data.name).data('food-id', foodId);
        variantSheet.find('.sheet-image').attr('src', data.image || '');
        const variantsDiv = variantSheet.find('.sheet-variants').empty();

        if (data.variants.length > 0) {
            data.variants.forEach((v, i) => {
                variantsDiv.append(`
                    <div class="variant-option">
                        <input type="radio" name="variant" id="variant${i}" value="${v.id}" ${i===0?'checked':''} data-price="${v.price}">
                        <label for="variant${i}">${v.name} - ₹${v.price}</label>
                    </div>
                `);
            });
        } else {
            variantsDiv.append(`<div class="variant-option single-variant">Regular - ₹${data.price}</div>`);
        }

        // Restore previous quantity
        const prevQty = cartItems[foodId] ? Object.values(cartItems[foodId].variants)[0]?.qty : 1;
        qty = prevQty || 1;
        $('#qty').text(qty);
        updateAddButton();

        variantSheet.addClass('active').show();
        overlay.addClass('active').show();
        $('body').addClass('no-scroll');
    });
}

// ===================== UPDATE ADD BUTTON =====================
function updateAddButton() {
    const selected = $('.sheet-variants input[type="radio"]:checked');
    let price = selected.length ? parseFloat(selected.data('price')) : 0;
    $('#add-to-cart').text(`Add item ₹${price * qty}`);
}
$(document).on('change', '.sheet-variants input[type="radio"]', updateAddButton);

// ===================== OPEN REPEAT SHEET =====================
function openRepeatSheet(foodId, lastVariantId) {
    const lastQty = cartItems[foodId].variants[lastVariantId].qty;
    const lastVariantText = cartItems[foodId].variants[lastVariantId].name || "Regular";

    repeatSheet.find('.sheet-name').text($(`.food-card[data-food-id="${foodId}"] .card-title`).text());
    repeatSheet.find('.sheet-image').attr('src', $(`.food-card[data-food-id="${foodId}"] .image-box img`).attr('src'));
    repeatSheet.find('.last-variant').html(`
        <div>${lastVariantText} x ${lastQty}</div>
        <button class="btn btn-success btn-sm" id="repeat-add">Add</button>
    `);

    repeatSheet.show().addClass('active');
    overlay.show().addClass('active');

    $('body').addClass('no-scroll');

    $('#repeat-sheet-close').off('click').on('click', () => closeSheet(repeatSheet));
    $('#repeat-add').off('click').on('click', () => {
        addVariantToCart(foodId, lastVariantId, lastQty);
        closeSheet(repeatSheet);
    });
    $('#add-new-customization').off('click').on('click', () => {
        closeSheet(repeatSheet);
        openVariantSheet(foodId);
    });
}

function openManageSheet(foodId) {

    repeatSheet.find('.sheet-name').text(
        $(`.food-card[data-food-id="${foodId}"] .card-title`).text()
    );

    const imageSrc = $(`.food-card[data-food-id="${foodId}"] .image-box img`).attr('src');
    repeatSheet.find('.sheet-image').attr('src', imageSrc);

    let html = '<h5>Manage your items</h5>';

    Object.entries(cartItems[foodId].variants).forEach(([variantId, data]) => {

        const variantName = data.name; // ✅ read from cartItems instead of DOM


        html += `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>${variantName}</div>
                <div>
                    <button class="btn btn-sm btn-outline-dark manage-minus" data-food="${foodId}" data-variant="${variantId}">-</button>
                    <span class="mx-2">${data.qty}</span>
                    <button class="btn btn-sm btn-outline-dark manage-plus" data-food="${foodId}" data-variant="${variantId}">+</button>
                </div>
            </div>
        `;
    });

    repeatSheet.find('.last-variant').html(html);

    repeatSheet.show().addClass('active');
    overlay.show().addClass('active');
    $('body').addClass('no-scroll');
}

$(document).on('click', '.manage-plus', function () {

    const foodId = $(this).data('food');
    const variantId = $(this).data('variant');

    cartItems[foodId].variants[variantId].qty += 1;

    addVariantToCart(foodId, variantId, 1);
    openManageSheet(foodId);
});

$(document).on('click', '.manage-minus', function () {

    const foodId = $(this).data('food');
    const variantId = $(this).data('variant');

    if (cartItems[foodId].variants[variantId].qty > 1) {
        cartItems[foodId].variants[variantId].qty -= 1;
    } else {
        delete cartItems[foodId].variants[variantId];
    }

    if (Object.keys(cartItems[foodId].variants).length === 0) {
        delete cartItems[foodId];
        closeSheet(repeatSheet);
    } else {
        openManageSheet(foodId);
    }

    updateCardUI(foodId);

    $.post(`/orders/remove_item/${foodId}/`, {
        variant_id: variantId,
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    });
});


// ===================== ADD VARIANT TO CART =====================
function addVariantToCart(foodId, variantId, quantity) {
    const card = $(`.food-card[data-food-id="${foodId}"]`);

    // Get variant name from DOM if available, fallback to "Regular"
    const variantName = card.find(`.sheet-variants input[value="${variantId}"]`).next('label').text() || "Regular";

    if (!cartItems[foodId]) cartItems[foodId] = {variants: {}, total_qty:0};

    if (!cartItems[foodId].variants[variantId]) {
        cartItems[foodId].variants[variantId] = {
            qty: 0,
            name: variantName   // ✅ store the name here
        };
    }

    cartItems[foodId].variants[variantId].qty += quantity;

    cartItems[foodId].total_qty = Object.values(cartItems[foodId].variants)
        .reduce((sum,v)=>sum+v.qty,0);

    updateCardUI(foodId);

    // Send AJAX to server
    $.post(`/orders/add_variant/${foodId}/`, {
        'variant_id': variantId,
        'quantity': quantity,
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
    });
}

// ===================== ADD BUTTON CLICK =====================
$(document).on('click', '.add-cart-btn', function () {
    const card = $(this).closest('.food-card');
    const foodId = card.data('food-id');
    const hasVariants = card.data('has-variants') == 1;

    if (hasVariants) {
        // if already added, show repeat sheet
        if (cartItems[foodId] && Object.keys(cartItems[foodId].variants).length > 0) {
            const lastVariantId = Object.keys(cartItems[foodId].variants)[0];
            openRepeatSheet(foodId, lastVariantId);
        } else {
            openVariantSheet(foodId);
        }
    } else {
        // normal item, just increment qty directly
        addVariantToCart(foodId, 'default', 1);
    }
});

// ===================== VARIANT SHEET ADD CLICK =====================
$('#add-to-cart').off('click').on('click', function () {
    const foodId = $('.sheet-name').data('food-id');
    const variantId = $('.sheet-variants input[type="radio"]:checked').val() || 'default';
    const quantity = parseInt($('#qty').text());

    addVariantToCart(foodId, variantId, quantity);
    closeSheet(variantSheet);
});

// ===================== PLUS / MINUS BUTTONS =====================
$(document).on('click', '.plus-btn', function () {
    const card = $(this).closest('.food-card');
    const foodId = card.data('food-id');
    const hasVariants = card.data('has-variants') == 1;

    if (hasVariants) {
        const variantIds = cartItems[foodId] ? Object.keys(cartItems[foodId].variants) : [];
        if (variantIds.length > 0) {
            const lastVariantId = variantIds[0];
            openRepeatSheet(foodId, lastVariantId);
        } else {
            openVariantSheet(foodId);
        }
    } else {
        addVariantToCart(foodId, 'default', 1);
    }
});

// $(document).on('click', '.minus-btn', function () {
//     const card = $(this).closest('.food-card');
//     const foodId = card.data('food-id');
//     const variantIds = cartItems[foodId] ? Object.keys(cartItems[foodId].variants) : ['default'];
//     const lastVariantId = variantIds[0];
//     let qtyToRemove = 1;

//     if (cartItems[foodId]?.variants[lastVariantId]?.qty > qtyToRemove) {
//         cartItems[foodId].variants[lastVariantId].qty -= qtyToRemove;
//     } else {
//         delete cartItems[foodId].variants[lastVariantId];
//         if (Object.keys(cartItems[foodId]?.variants || {}).length === 0) delete cartItems[foodId];
//     }

//     if (cartItems[foodId]) cartItems[foodId].total_qty = Object.values(cartItems[foodId].variants)
//         .reduce((sum,v)=>sum+v.qty,0);

//     updateCardUI(foodId);

//     $.post(`/orders/remove_item/${foodId}/`, {
//         'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
//     });
// });
$(document).on('click', '.minus-btn', function () {

    const card = $(this).closest('.food-card');
    const foodId = card.data('food-id');
    const hasVariants = card.data('has-variants') == 1;

    if (!cartItems[foodId]) return;

    const variantIds = Object.keys(cartItems[foodId].variants);

    // 🟢 If multiple variants → open manage sheet
    if (hasVariants && variantIds.length > 1) {
        openManageSheet(foodId);
        return;
    }

    // 🟢 If single variant → decrease directly
    const variantId = variantIds[0];

    if (cartItems[foodId].variants[variantId].qty > 1) {
        cartItems[foodId].variants[variantId].qty -= 1;
    } else {
        delete cartItems[foodId].variants[variantId];
        if (Object.keys(cartItems[foodId].variants).length === 0) {
            delete cartItems[foodId];
        }
    }

    updateCardUI(foodId);

    $.post(`/orders/remove_item/${foodId}/`, {
        variant_id: variantId,
        csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
    });

});

// ===================== BOTTOM SHEET QTY BUTTONS =====================
$('#qty-increase').click(() => { qty++; $('#qty').text(qty); updateAddButton(); });
$('#qty-decrease').click(() => { if(qty>1) qty--; $('#qty').text(qty); updateAddButton(); });

// ===================== CLOSE SHEETS =====================
function closeSheet(sheetToClose) {
    sheetToClose.removeClass('active').hide();
    overlay.removeClass('active').hide();
    $('body').removeClass('no-scroll');
    qty = 1;
    $('#qty').text(qty);
}
overlay.click(() => {
    closeSheet(variantSheet);
    closeSheet(repeatSheet);
});

// ===================== RESTORE CART ON PAGE LOAD =====================
$(document).ready(function () {
    Object.keys(cartItems).forEach(foodId => updateCardUI(foodId));
});



$(document).on('click', '.add-cart-btn', function () {
    const card = $(this).closest('.food-card');
    const foodId = card.data('food-id');
    const hasVariants = card.data('has-variants') == 1;

    if (hasVariants) {
        if (cartItems[foodId] && Object.keys(cartItems[foodId].variants).length > 0) {
            // open repeat sheet
            const lastVariantId = Object.keys(cartItems[foodId].variants)[0];
            openRepeatSheet(foodId, lastVariantId);
        } else {
            // open variant sheet first time
            openVariantSheet(foodId);
        }
    } else {
        // normal item → old working logic
        addVariantToCart(foodId, 'default', 1);
    }
});
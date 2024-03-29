function collectSelectedProducts() {
    const selectedProducts = [];
    document.querySelectorAll('input[name="selected_product"]:checked').forEach(checkbox => {
        selectedProducts.push(checkbox.value);
    });
    return selectedProducts;
}
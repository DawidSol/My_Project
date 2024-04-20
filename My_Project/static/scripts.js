    function geoFindMe(callback) {
    const status = document.querySelector("#status");
    const mapLink = document.querySelector("#map-link");
    mapLink.href = "";
    mapLink.textContent = "";
    function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;
    document.getElementById("latitude").value = latitude;
    document.getElementById("longitude").value = longitude;
        status.textContent = "";
        mapLink.href = `https://www.openstreetmap.org/#map=18/${latitude}/${longitude}`;
        mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
        if (callback) {
                callback(latitude, longitude);
            }
}
    function error() {
    status.textContent = "Unable to retrieve your location";
}
    if (!navigator.geolocation) {
    status.textContent = "Geolocation is not supported by your browser";
} else {
    status.textContent = "Locating…";
    navigator.geolocation.getCurrentPosition(success, error);
}
}
    document.addEventListener("DOMContentLoaded", function() {
        document.querySelector("#find-me").addEventListener("click", function () {
            geoFindMe();
        });
    });
    document.querySelector("#my-location").addEventListener("click", function() {
            const myLocationButton = document.getElementById('my-location');
    myLocationButton.addEventListener('click', function() {
        const shoppingListId = myLocationButton.getAttribute('data-shopping-list-id');
            geoFindMe(function(latitude, longitude) {
                window.location.href = `/send_reminder/${shoppingListId}/?latitude=${latitude}&longitude=${longitude}`;
            });
        });
});
const defaultCoordinates = [52.2297, 21.0122];
const defaultZoomLevel = 15;
const mymap = L.map('mapid').setView(defaultCoordinates, defaultZoomLevel);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(mymap);
mymap.on('click', function (e) {
    const latitude = e.latlng.lat;
    const longitude = e.latlng.lng;
    document.getElementById('latitude').value = latitude;
    document.getElementById('longitude').value = longitude;
});

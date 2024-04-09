function geoFindLocation(city, street) {
            const status = document.querySelector("#status");
            const mapLink = document.querySelector("#map-link");
            mapLink.href = "";
            mapLink.textContent = "";
            const address = city + ", " + street;
            const url = `https://nominatim.openstreetmap.org/search?q=${address}&format=json&limit=1`;

            fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    const latitude = data[0].lat;
                    const longitude = data[0].lon;
                    document.getElementById("latitude").value = latitude;
                    document.getElementById("longitude").value = longitude;
                    status.textContent = "";
                    mapLink.href = `https://www.openstreetmap.org/#map=18/${latitude}/${longitude}`;
                    mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
                } else {
                    status.textContent = "Nie znaleziono współrzędnych dla podanego adresu.";
                }
            })
            .catch(error => {
                status.textContent = "Wystąpił błąd podczas geokodowania adresu.";
            });
        }
        document.querySelector("#geocode-button").addEventListener("click", function() {
            const city = document.getElementById("city-input").value;
            const street = document.getElementById("street-input").value;
            geoFindLocation(city, street);
        });
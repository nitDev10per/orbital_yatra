
let coordinates;
let start_date;
let end_date;

let latLng;

function initMap() {
    // Initialize map
    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -34.397, lng: 150.644 },
        zoom: 8,
    });

    // Search Box
    const input = document.getElementById("search-box");
    const searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener("bounds_changed", () => {
        searchBox.setBounds(map.getBounds());
    });

    let markers = [];
    let selectedMarker = null; // Variable to hold the currently selected marker

    // Listen for the event fired when the user selects a prediction and retrieve more details
    searchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places.length === 0) {
            return;
        }

        // Clear out the old markers.
        markers.forEach((marker) => marker.setMap(null));
        markers = [];

        // For each place, get the icon, name, and location.
        const bounds = new google.maps.LatLngBounds();
        places.forEach((place) => {
            if (!place.geometry || !place.geometry.location) {
                return;
            }

            const marker = new google.maps.Marker({
                map,
                title: place.name,
                position: place.geometry.location,
            });

            markers.push(marker);

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
    });

    // Display Latitude and Longitude when the map is clicked
    map.addListener('click', function (mapsMouseEvent) {
        latLng = mapsMouseEvent.latLng;

        // Remove the previous marker if it exists
        if (selectedMarker) {
            selectedMarker.setMap(null);
        }

        // Create a new marker at the clicked location
        selectedMarker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: 'Selected Location'
        });

        // Get today's date and the date one year before today
        const endDate = new Date();
        const startDate = new Date();
        startDate.setFullYear(endDate.getFullYear() - 1);

        // Format the dates as YYYY-MM-DD
        const formattedEndDate = endDate.toISOString().split('T')[0];
        const formattedStartDate = startDate.toISOString().split('T')[0];
        start_date=formattedStartDate;
        end_date=formattedEndDate;
        coordinates=[latLng.lat(),latLng.lng()]
        // Update the coordinates display
        document.getElementById('coordinates').innerText =
            'Latitude: ' + latLng.lat() + ', Longitude: ' + latLng.lng() +
            ', Start Date: ' + formattedStartDate + ', End Date: ' + formattedEndDate;
    });

    // Handle Current Location Button
    const locationButton = document.getElementById('current-location-btn');
    locationButton.addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };

                    // Center the map at the user's current location
                    map.setCenter(pos);
                    map.setZoom(14);

                    // Add a marker for the current location
                    new google.maps.Marker({
                        position: pos,
                        map: map,
                        title: "Your Current Location",
                    });

                    // Display the current coordinates
                    document.getElementById('coordinates').innerText =
                        'Current Location: Latitude: ' + pos.lat + ', Longitude: ' + pos.lng;
                },
                () => {
                    alert("Geolocation failed. Please allow location access.");
                }
            );
        } else {
            alert("Your browser doesn't support Geolocation.");
        }

        
   
    });

     // Function to add WMS Layer
    


    // Add the WMS layer to the map using the API response
    
}

function addWmsLayer(tileUrl) {
    const map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -34.397, lng: 150.644 },
        zoom: 8,
    });
    const input = document.getElementById("search-box");
    const searchBox = new google.maps.places.SearchBox(input);
    map.controls[google.maps.ControlPosition.TOP_CENTER].push(input);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener("bounds_changed", () => {
        searchBox.setBounds(map.getBounds());
    });

    let markers = [];
    let selectedMarker = null; // Variable to hold the currently selected marker

    // Listen for the event fired when the user selects a prediction and retrieve more details
    searchBox.addListener("places_changed", () => {
        const places = searchBox.getPlaces();

        if (places.length === 0) {
            return;
        }

        // Clear out the old markers.
        markers.forEach((marker) => marker.setMap(null));
        markers = [];

        // For each place, get the icon, name, and location.
        const bounds = new google.maps.LatLngBounds();
        places.forEach((place) => {
            if (!place.geometry || !place.geometry.location) {
                return;
            }

            const marker = new google.maps.Marker({
                map,
                title: place.name,
                position: place.geometry.location,
            });

            markers.push(marker);

            if (place.geometry.viewport) {
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }
        });
        map.fitBounds(bounds);
    });

    // Display Latitude and Longitude when the map is clicked
    map.addListener('click', function (mapsMouseEvent) {
        latLng = mapsMouseEvent.latLng;

        // Remove the previous marker if it exists
        if (selectedMarker) {
            selectedMarker.setMap(null);
        }

        // Create a new marker at the clicked location
        selectedMarker = new google.maps.Marker({
            position: latLng,
            map: map,
            title: 'Selected Location'
        });

        // Get today's date and the date one year before today
        const endDate = new Date();
        const startDate = new Date();
        startDate.setFullYear(endDate.getFullYear() - 1);

        // Format the dates as YYYY-MM-DD
        const formattedEndDate = endDate.toISOString().split('T')[0];
        const formattedStartDate = startDate.toISOString().split('T')[0];
        start_date=formattedStartDate;
        end_date=formattedEndDate;
        coordinates=[latLng.lat(),latLng.lng()]
        // Update the coordinates display
        document.getElementById('coordinates').innerText =
            'Latitude: ' + latLng.lat() + ', Longitude: ' + latLng.lng() +
            ', Start Date: ' + formattedStartDate + ', End Date: ' + formattedEndDate;
    });

    // Handle Current Location Button
    const locationButton = document.getElementById('current-location-btn');
    locationButton.addEventListener('click', () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };

                    // Center the map at the user's current location
                    map.setCenter(pos);
                    map.setZoom(14);

                    // Add a marker for the current location
                    new google.maps.Marker({
                        position: pos,
                        map: map,
                        title: "Your Current Location",
                    });

                    // Display the current coordinates
                    document.getElementById('coordinates').innerText =
                        'Current Location: Latitude: ' + pos.lat + ', Longitude: ' + pos.lng;
                },
                () => {
                    alert("Geolocation failed. Please allow location access.");
                }
            );
        } else {
            alert("Your browser doesn't support Geolocation.");
        }

        
   
    });
    const wmsLayer = new google.maps.ImageMapType({
        getTileUrl: function(coord, zoom) {
            const proj = map.getProjection();
            const zfactor = Math.pow(2, zoom);

            // Get the bounding box for the tile
            const topLeft = proj.fromPointToLatLng(
                new google.maps.Point(coord.x * 256 / zfactor, coord.y * 256 / zfactor)
            );
            const bottomRight = proj.fromPointToLatLng(
                new google.maps.Point((coord.x + 1) * 256 / zfactor, (coord.y + 1) * 256 / zfactor)
            );

            // Build the WMS request URL with the bounding box and other parameters
            return tileUrl +
                `?SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&LAYERS=your_layer_name` + // Replace `your_layer_name`
                `&STYLES=&FORMAT=image/png&SRS=EPSG:4326&WIDTH=256&HEIGHT=256` +
                `&BBOX=${bottomRight.lng()},${bottomRight.lat()},${topLeft.lng()},${topLeft.lat()}`;
        },
        tileSize: new google.maps.Size(256, 256),
        opacity: 0.6,
    });

    map.overlayMapTypes.push(wmsLayer); // Add the WMS layer to the map
}



async function fetchWeatherData(lat, lng) {
    const proxyUrl = 'http://localhost:3000/fetch?url='; // Your local proxy
    const apiUrl = `https://api.meteomatics.com/2024-10-06T00:00:00Z--2024-10-09T00:00:00Z:PT1H/t_2m:C,precip_1h:mm,wind_speed_10m:ms/${lat},${lng}/json`;
    const url = proxyUrl + encodeURIComponent(apiUrl);

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        plotData(data);
    } catch (error) {
        console.error('Error fetching weather data:', error);
        document.getElementById('weatherData').innerText = 'Error fetching weather data. Please check the console for details.';
    }
}

function plotData(data) {
    const labels = [];
    const temperatureData = [];
    const precipitationData = [];
    const windSpeedData = [];

    data.data.forEach(parameter => {
        parameter.coordinates.forEach(coord => {
            coord.dates.forEach(entry => {
                const date = new Date(entry.date).toLocaleString();
                labels.push(date);

                if (parameter.parameter === 't_2m:C') {
                    temperatureData.push(entry.value);
                } else if (parameter.parameter === 'precip_1h:mm') {
                    precipitationData.push(entry.value);
                } else if (parameter.parameter === 'wind_speed_10m:ms') {
                    windSpeedData.push(entry.value);
                }
            });
        });
    });

    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: temperatureData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                },
                {
                    label: 'Precipitation (mm)',
                    data: precipitationData,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                },
                {
                    label: 'Wind Speed (m/s)',
                    data: windSpeedData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}



function submit() {
    // fetchWeatherData(37.7749, -122.4194)
   
    // Check if elements exist
    const container = document.getElementById('container');
    const container2 = document.getElementById('container2');
    const rightBox = document.getElementById('right-box');
    const bottomBox = document.getElementById('bottom-box');
    const submitButton = document.getElementById('submit'); // Get the button element, not its inner text

    // Log elements for debugging
    console.log('Container:', container);
    console.log('Container2:', container2);

    // Get the user's input
    const input = document.getElementById('coordinates').innerText;

    // Ensure elements are found before trying to access their styles
    if (container && rightBox && bottomBox && submitButton) {
        const isSubmit = submitButton.innerText === 'Submit';

        rightBox.style.display = isSubmit ? 'block' : 'none';
        bottomBox.style.display = isSubmit ? 'flex' : 'none';

        submitButton.innerText = isSubmit ? 'Back' : 'Submit'; // Change button text
    } else {
        console.error('One or more elements not found!');
    }

    console.log(input);
    fetchApi();
    
}

function updateValueDisplay(value) {
    document.getElementById('slider-value').innerText = value;
}

// async function fetchApi() {
    

//     // Get the coordinates from the input
//     // const coordinates = JSON.stringify(coordinates); // Assuming the input is a JSON string
//     // const start_date = start_date; // Modify as needed
//     // const end_date = end_date;   // Modify as needed
//      const cloud_cover = document.getElementById('value-slider').value;

//     // Create a FormData object
//     const formData = new FormData();
//     formData.append('coordinates', JSON.stringify(coordinates)); // Send as JSON string
//     formData.append('start_date', start_date);
//     formData.append('end_date', end_date);
//     formData.append('cloud_cover', cloud_cover);

//     try {
//         const response = await fetch('http://127.0.0.1:7000/request', {
//             method: 'POST',
//             body: formData // Send the FormData object
//         });

//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }

//         const data = await response.json();
//         console.log('data', data);
//         document.getElementById('responceOutput').innerHTML = data.pixel_values_landsat[0];
//         plotPixelValues(data.pixel_values_landsat);
    

//         //plotPixelValues(data.pixel_values_landsat);
//     } catch (error) {
//         console.error('Error fetching data:', error);
//         // document.getElementById('responseOutput').textContent = 'Error fetching data. Check console for details.';
//     }
// }
async function fetchApi() {
    const cloud_cover = document.getElementById('value-slider').value;

    const formData = new FormData();
    formData.append('coordinates', JSON.stringify(coordinates));
    formData.append('start_date', start_date);
    formData.append('end_date', end_date);
    formData.append('cloud_cover', cloud_cover);

    try {
        const response = await fetch('http://127.0.0.1:7000/request', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('data', data);  // Log data in the console fdebugging


        plotPixelValues(data.pixel_values_landsat);  // Call charfuncwith 


        populateTable(data.pass_dates_landsat);
        // await loadXML(data.metadata_path)
        await loadTextFile(data.metadata_path);
        
        //addWmsLayer(data.tile_url);
        // Check if responseOutput element exists and update it
        const responseOutput = document.getElementById('responseOutput');
        if (responseOutput) {
            if (data.pixel_values_landsat && data.pixel_values_landsat.length > 0) {
                responseOutput.innerHTML = 'Pixel Values: ' + JSON.stringify(data.pixel_values_landsat);
                
            } else {
                console.error('No pixel values found in the response');
                responseOutput.innerText = 'No pixel values found.';
            }
        } else {
            console.error('Element with ID "responseOutput" not found!');
        }
        
    } catch (error) {
        console.error('Error fetching data:', error);
        const responseOutput = document.getElementById('responseOutput');
        if (responseOutput) {
            responseOutput.innerText = 'Error fetching data. Check console for details.';
        }
    }
}

function populateTable(pass_dates_landsat) {
    const tableBody = document.getElementById('landsatTableBody');
    
    pass_dates_landsat.forEach((item) => {
        const row = document.createElement('tr');

        // Create and insert the Date cell
        const dateCell = document.createElement('td');
        dateCell.textContent = new Date(item.Date).toDateString();
        row.appendChild(dateCell);

        // Create and insert the Platform cell
        const platformCell = document.createElement('td');
        platformCell.textContent = item.Platform;
        row.appendChild(platformCell);

        // Create and insert the Time cell
        const timeCell = document.createElement('td');
        timeCell.textContent = item["Time (+/- 00:15:00 hrs)"];
        row.appendChild(timeCell);

        // Append the row to the table body
        tableBody.appendChild(row);
    });
}

async function loadTextFile(path) {
    // Assuming the path is to a .txt file
    console.log('Loading text file from path:', path);
    try {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const text = await response.text();
        // Display the text data in the xmlData div
        document.getElementById('xmlData').textContent = text;
    } catch (error) {
        console.error("Error fetching text file:", error);
        document.getElementById('xmlData').textContent = 'Error fetching text file.';
    }
}

// async function loadXML(path) {
//      const xmlPath = "D:\NASA space apps challenge 2024\Space-Apps\static\Metadata\mtl.xml"; 
//     // Adjust for Node.js server if necessary
//     console.log('Loading XML from path:', xmlPath);
//     try {
//         const response = await fetch(path);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
        
//         const xmlText = await response.text();
//         convertXMLToJSON(xmlText);
//     } catch (error) {
//         console.error("Error fetching XML file:", error);
//         document.getElementById('xmlData').textContent = 'Error fetching XML file.';
//     }
// }

// function convertXMLToJSON(xml) {
//     const parser = new Parser();
    
//     parser.parseString(xml, (err, result) => {
//         if (err) {
//             console.error("Error parsing XML:", err);
//             document.getElementById('xmlData').textContent = 'Error parsing XML file.';
//             return;
//         }
        
//         const json = JSON.stringify(result, null, 2);
//         console.log("JSON Output:", json);
        
//         // Optionally, display the JSON in an element on the page
//         document.getElementById('jsonData').textContent = json;
//     });
// }


function plotPixelValues(data) {
    const labels = data.map(band => band.Band);
    const values = data.map(band => band.Value);

    console.log("Plotting chart with labels:", labels);  // Log the labels for the chart
    console.log("Plotting chart with values:", values);  // Log the values for the chart

    const ctx = document.getElementById('pixelValuesChart').getContext('2d');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Pixel Values',
                    data: values,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Pixel Value'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Bands'
                        }
                    }
                }
            }
        });
    } else {
        console.error("Canvas element for chart not found!");
    }
}



// Attach the event listener to the form






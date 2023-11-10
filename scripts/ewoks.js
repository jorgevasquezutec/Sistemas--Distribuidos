import http from 'k6/http';

export let options = {
    vus: 20, // Número de usuarios virtuales (hilos) que ejecutarán las solicitudes en paralelo
    iterations: 20, // Número total de solicitudes a realizar
};

export default function () {
    // URL de la API que quieres probar
    const apiUrl = 'http://192.168.1.60:5000/v1/anime?title=naruto';

    // Cada usuario virtual realizará una solicitud
    const response = http.get(apiUrl);
    // const data = JSON.parse(response.body);
    // console.log(data);
    // console.log(`Respuesta: ${response.body}`);

    // Registra el estado de la respuesta
    console.log(`Respuesta: ${response.status}`
);
}
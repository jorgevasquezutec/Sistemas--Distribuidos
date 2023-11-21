import http from 'k6/http';
import { randomItem } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

export let options = {
    vus: 100, // Número de usuarios virtuales (hilos) que ejecutarán las solicitudes en paralelo
    iterations: 100, // Número total de solicitudes a realizar
    duration: '1m', // Duración de la prueba
};
const titles = ['trigun', 'monster', 'naruto', 'zipang', 'sunabouzu', 'akira', 'avenger', 'beck', 'chobits'];
// const titles = ['naruto']

export default function () {

    const randomTitle = randomItem(titles);
    // console.log(`Título: ${randomTitle}`);
    // const randomTitle = titles[Math.floor(Math.random() * titles.length)];
    // URL de la API que quieres probar
    const apiUrl = `http://192.168.1.52:5000/v1/janime?title=${randomTitle}`;

    // Cada usuario virtual realizará una solicitud
    const response = http.get(apiUrl);
    const data = JSON.parse(response.body);
    console.log(data);
    // console.log(`Respuesta: ${response.body}`);

    // Registra el estado de la respuesta
    console.log(`Respuesta: ${response.status}`
);
}
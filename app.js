// app.js - Frontend para Security API Exercise
// La variable API_KEY se inyecta desde el entrypoint del contenedor
const API_KEY = "mT8dmpumiGhSqmr8zmWmiv_Dg7adotoDPq8iAmHeT-Q";

// Referencias a elementos del DOM
const getBtn = document.getElementById('getBtn');
const postBtn = document.getElementById('postBtn');
const responseDisplay = document.getElementById('responseDisplay');

// --- Funciones auxiliares ---

/**
 * Muestra datos en el área de respuesta.
 * @param {any} data - Objeto o string a mostrar.
 */
const displayResponse = (data) => {
    if (typeof data === 'object') {
        responseDisplay.textContent = JSON.stringify(data, null, 2);
    } else {
        responseDisplay.textContent = data;
    }
};

/**
 * Construye las opciones para fetch con el header x-api-key.
 * @param {string} method - Método HTTP (GET, POST, etc.)
 * @param {object|null} body - Cuerpo de la petición (opcional).
 * @returns {object} Opciones para fetch.
 */
const getFetchOptions = (method, body = null) => {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
        }
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    return options;
};

// --- Endpoints de autenticación (originales) ---

/**
 * GET /api/data - Obtiene datos protegidos.
 */
const getProtectedData = async () => {
    try {
        const response = await fetch('/api/data', getFetchOptions('GET'));
        const data = await response.json();
        if (!response.ok) {
            displayResponse(`Error ${response.status}: ${data.error || 'Something went wrong'}`);
            return;
        }
        displayResponse(data);
    } catch (error) {
        displayResponse(`Network error: ${error.message}`);
    }
};

/**
 * POST /api/data - Envía datos protegidos.
 */
const postProtectedData = async () => {
    try {
        const response = await fetch('/api/data', getFetchOptions('POST', { sample: 'data' }));
        const data = await response.json();
        if (!response.ok) {
            displayResponse(`Error ${response.status}: ${data.error || 'Something went wrong'}`);
            return;
        }
        displayResponse(data);
    } catch (error) {
        displayResponse(`Network error: ${error.message}`);
    }
};

// --- Nuevos endpoints de cifrado/descifrado (integración con crypto_service) ---

/**
 * POST /api/secrets - Guarda un secreto cifrado.
 * Envía { name, value } y recibe { id, message }.
 */
const createSecret = async () => {
    const name = prompt("Enter a name for the secret:");
    if (!name) return;
    const value = prompt("Enter the secret value:");
    if (!value) return;

    try {
        const response = await fetch('/api/secrets', getFetchOptions('POST', { name, value }));
        const data = await response.json();
        if (!response.ok) {
            displayResponse(`Error ${response.status}: ${data.error || 'Failed to store secret'}`);
            return;
        }
        displayResponse(data);
    } catch (error) {
        displayResponse(`Network error: ${error.message}`);
    }
};

/**
 * GET /api/secrets/:id - Recupera un secreto y lo descifra.
 * Pide el ID al usuario.
 */
const getSecret = async () => {
    const id = prompt("Enter the secret ID to retrieve:");
    if (!id) return;

    try {
        const response = await fetch(`/api/secrets/${id}`, getFetchOptions('GET'));
        const data = await response.json();
        if (!response.ok) {
            displayResponse(`Error ${response.status}: ${data.error || 'Secret not found'}`);
            return;
        }
        displayResponse(data);
    } catch (error) {
        displayResponse(`Network error: ${error.message}`);
    }
};

// --- Asignación de eventos ---

// Eventos para los botones originales
getBtn.addEventListener('click', getProtectedData);
postBtn.addEventListener('click', postProtectedData);

// Botones adicionales (debes agregarlos en el HTML si quieres probar cifrado)
// Puedes descomentar estas líneas y agregar botones en el HTML con los ids:
// <button id="createSecretBtn">Create Secret</button>
// <button id="getSecretBtn">Get Secret</button>
// document.getElementById('createSecretBtn')?.addEventListener('click', createSecret);
// document.getElementById('getSecretBtn')?.addEventListener('click', getSecret);

// Mensaje inicial
displayResponse('Ready. Click a button to call the API.');
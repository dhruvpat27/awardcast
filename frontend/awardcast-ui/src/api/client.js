import axios from 'axios';

const client = axios.create({
    baseURL: 'https://awardcast-production.up.railway.app',
});

export default client;
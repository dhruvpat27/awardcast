import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

document.body.style.backgroundColor = '#0f0f1a';
document.body.style.color = 'white';
document.body.style.margin = '0';
document.body.style.fontFamily = 'sans-serif';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
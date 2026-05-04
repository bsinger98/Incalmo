import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App'
import reportWebVitals from './reportWebVitals';

// ResizeObserver fires benign notifications when canvas layout shifts; suppress
// them so the CRA dev-server error overlay doesn't block the UI.
window.addEventListener('error', (e) => {
  if (String(e.message).includes('ResizeObserver')) e.stopImmediatePropagation();
}, true);

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
import React from 'react';

export default function Page404() {
    return (
        <div>
        <h1>404 - Page not found</h1>
        <p>The page you are looking for might have been removed, had its name changed or is temporarily unavailable.</p>
        {/*image crying from pulic folder*/}
        <img src="/crying.jpg" alt="Crying emoji" style={{ width: '500px', height: '250px' }} />
        </div>
    );
    }
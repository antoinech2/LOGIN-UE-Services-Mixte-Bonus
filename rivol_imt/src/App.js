import * as React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Bookings from "./routes/Bookings";

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/bookings" element={<Bookings date={"20151202"}/>} />
            </Routes>
        </BrowserRouter>
    );
}

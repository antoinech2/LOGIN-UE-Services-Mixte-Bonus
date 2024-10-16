import * as React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Bookings from "./routes/Bookings";
import Home from "./routes/Home";
import Page404 from "./routes/Page404";

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/bookings" element={<Bookings date={"20151202"}/>} />
                <Route path="/" element={<Home />} />
                <Route path="*" element={<Page404 />} />
            </Routes>
        </BrowserRouter>
    );
}

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { App } from "./App";
import { RoleProvider } from "./contexts/RoleContext";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <RoleProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </RoleProvider>
  </React.StrictMode>
);

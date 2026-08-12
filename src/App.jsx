// src/App.jsx

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import GriffinConsole from "./components/console/GriffinConsole";
import AnalysisWorkspace from "./components/workspace/AnalysisWorkspace";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Default */}
        <Route
          path="/"
          element={
            <Navigate
              to="/console"
              replace
            />
          }
        />

        {/* Main Griffin Console */}
        <Route
          path="/console"
          element={<GriffinConsole />}
        />

        {/* Direct evaluation */}
        <Route
          path="/analysis/:evaluationId"
          element={<AnalysisWorkspace />}
        />

        {/* Unknown route */}
        <Route
          path="*"
          element={
            <Navigate
              to="/console"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
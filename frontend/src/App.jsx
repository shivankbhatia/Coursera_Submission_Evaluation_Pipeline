import { Routes, Route, Link } from "react-router-dom";
import FailureReasons from "./pages/FailureReasons";
import HomePage from "./pages/HomePage";
import { useState } from "react";


function App() {
  const [roll, setRoll] = useState("");
  const [records, setRecords] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [serviceDown, setServiceDown] = useState(false);
  const [currentStudent, setCurrentStudent] = useState(null);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-800 
                    dark:bg-gray-900 dark:text-gray-100 transition-colors duration-300">

      {/* Navbar */}
      <nav className="bg-white dark:bg-gray-800 shadow-sm py-4 transition-colors duration-300">
        <div className="container mx-auto px-4 flex justify-between items-center">

          <Link
            to="/"
            className="text-2xl font-bold text-blue-600 hover:text-blue-700 transition"
          >
            Guided Project Status
          </Link>

          <Link
            to="/failure-reasons"
            className="w-9 h-9 flex items-center justify-center 
                       rounded-full bg-blue-600 text-white 
                       font-bold text-lg 
                       hover:bg-blue-700 transition"
          >
            ?
          </Link>

        </div>
      </nav>

      {/* Production Disclaimer */}
      <div className="text-center text-sm italic 
                      text-gray-500 dark:text-gray-400 
                      mt-3">
        This system is currently under production and may occasionally produce irregular results.
      </div>

      <Routes>
        <Route
          path="/"
          element={
            <HomePage
              roll={roll}
              setRoll={setRoll}
              records={records}
              setRecords={setRecords}
              isStreaming={isStreaming}
              setIsStreaming={setIsStreaming}
              errorMessage={errorMessage}
              setErrorMessage={setErrorMessage}
              serviceDown={serviceDown}
              setServiceDown={setServiceDown}
              currentStudent={currentStudent}
              setCurrentStudent={setCurrentStudent}
            />
          }
        />
        <Route path="/failure-reasons" element={<FailureReasons />} />
      </Routes>

    </div>
  );
}

export default App;

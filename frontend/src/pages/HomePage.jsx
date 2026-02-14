import { useState } from "react";

/* ---------------- Loading Dots Component ---------------- */
function LoadingDots() {
  return (
    <span className="inline-flex ml-1">
      <span className="animate-bounce [animation-delay:-0.3s]">.</span>
      <span className="animate-bounce [animation-delay:-0.15s]">.</span>
      <span className="animate-bounce">.</span>
    </span>
  );
}

function HomePage({
  roll,
  setRoll,
  records,
  setRecords,
  isStreaming,
  setIsStreaming,
  errorMessage,
  setErrorMessage,
  serviceDown,
  setServiceDown,
  currentStudent,
  setCurrentStudent
}) {

  const handleEvaluate = () => {
    if (!roll) {
      setErrorMessage("Please enter a roll number.");
      return;
    }

    setRecords([]);
    setErrorMessage(null);
    setServiceDown(false);
    setCurrentStudent(null);
    setIsStreaming(true);

    let connectionEstablished = false;

    const eventSource = new EventSource(
      `http://localhost:8000/evaluate-stream/${roll}`
    );

    eventSource.onopen = () => {
      connectionEstablished = true;
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.error) {
        setErrorMessage("No records found for this roll number.");
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      if (data.done) {
        eventSource.close();
        setIsStreaming(false);
        return;
      }

      setRecords((prev) => {
        const updated = [...prev];

        if (!updated[data.row_id]) {
          updated[data.row_id] = {
            status: data.status,
            result: null,
          };
        } else {
          updated[data.row_id].status = data.status;
        }

        if (data.result) {
          updated[data.row_id].result = data.result;

          if (!currentStudent && data.result.full_name) {
            setCurrentStudent(data.result.full_name);
          }
        }

        return updated;
      });
    };

    eventSource.onerror = () => {
      eventSource.close();
      setIsStreaming(false);

      if (!connectionEstablished) {
        setServiceDown(true);
      }
    };
  };

  /* ---------------- PASS + MARKS CALCULATION ---------------- */

  const passCount = records.filter(
    (r) => r.result?.verdict === "PASS"
  ).length;

  const calculateMarks = (passes) => {
    if (passes >= 24) return 8;
    if (passes >= 22) return 7;
    if (passes >= 18) return 6;
    if (passes >= 15) return 5;
    if (passes >= 12) return 4;
    if (passes >= 10) return 3;
    if (passes >= 8) return 2;
    if (passes >= 5) return 1;
    return 0;
  };

  const marks = calculateMarks(passCount);

  const allEvaluated =
    records.length > 0 &&
    records.every((r) => r.result?.verdict);

  return (
    <div className="transition-colors duration-300">

      {/* Input Section */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-md mx-auto bg-white dark:bg-gray-800 shadow rounded-lg p-6 transition-colors duration-300">
          <h3 className="text-lg font-semibold mb-4 text-center">
            Evaluate Student Records
          </h3>

          <input
            className="w-full border border-gray-300 dark:border-gray-600 
                       bg-white dark:bg-gray-700 
                       text-gray-800 dark:text-gray-100
                       rounded px-3 py-2 
                       focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter Roll Number"
            value={roll}
            onChange={(e) => setRoll(e.target.value)}
          />

          <button
            onClick={handleEvaluate}
            disabled={isStreaming}
            className="mt-4 w-full bg-blue-600 text-white py-2 rounded 
                       font-semibold hover:bg-blue-700 transition 
                       disabled:opacity-60"
          >
            {isStreaming ? (
              <>
                Processing
                <LoadingDots />
              </>
            ) : (
              "Evaluate"
            )}
          </button>
        </div>
      </div>

      {/* Student Name */}
      {currentStudent && (
        <div className="container mx-auto px-4">
          <p className="text-lg font-semibold">
            Student:{" "}
            <span className="text-blue-600">
              {currentStudent}
            </span>
          </p>
        </div>
      )}

      {/* Errors */}
      {errorMessage && (
        <div className="max-w-md mx-auto mt-4 bg-yellow-100 text-yellow-700 px-4 py-3 rounded">
          {errorMessage}
        </div>
      )}

      {serviceDown && (
        <div className="max-w-md mx-auto mt-4 bg-red-100 text-red-700 px-4 py-3 rounded">
          Service is currently unavailable. Please try again later.
        </div>
      )}

      {/* Results Table */}
      {records.length > 0 && (
        <div className="container mx-auto px-4 py-8">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-x-auto transition-colors duration-300">

            <table className="min-w-full text-sm text-left">
              <thead className="bg-gray-50 dark:bg-gray-700 border-b dark:border-gray-600">
                <tr>
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Project</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Verdict</th>
                  <th className="px-4 py-3">Reason</th>
                </tr>
              </thead>

              <tbody>
                {records.map((rec, idx) => (
                  <tr
                    key={idx}
                    className="border-b dark:border-gray-700"
                  >
                    <td className="px-4 py-3">{idx + 1}</td>

                    <td className="px-4 py-3">
                      {rec.result?.project || "-"}
                    </td>

                    <td className="px-4 py-3">
                      {rec.status ===
                      "LLM Validation (may take 1-2 minutes)" ? (
                        <span className="text-yellow-600 font-medium">
                          {rec.status}
                        </span>
                      ) : (
                        rec.status
                      )}
                    </td>

                    <td className="px-4 py-3 font-semibold">
                      {rec.result?.verdict === "PASS" && (
                        <span className="text-green-600">PASS</span>
                      )}
                      {rec.result?.verdict === "FAIL" && (
                        <span className="text-red-600">FAIL</span>
                      )}
                      {!rec.result?.verdict && "-"}
                    </td>

                    <td className="px-4 py-3 text-red-500">
                      {rec.result?.reason || "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Final Grading Section */}
      {!isStreaming && allEvaluated && (
        <div className="container mx-auto px-4 pb-12">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mt-6 transition-colors duration-300">

            <h3 className="text-lg font-semibold mb-4">
              Final Evaluation Result
            </h3>

            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">

              <div>
                <p>
                  Total Projects Passed:
                  <span className="font-semibold text-green-600 ml-2">
                    {passCount}
                  </span>
                </p>

                <p className="mt-2">
                  Total Projects Failed:
                  <span className="font-semibold text-red-600 ml-2">
                    {records.length - passCount}
                  </span>
                </p>
              </div>

              <div className="text-center md:text-right">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Final Marks
                </p>
                <p className="text-3xl font-bold text-blue-600">
                  {marks} / 8
                </p>
              </div>

            </div>

            <div className="mt-6">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-5 overflow-hidden">
                <div
                  className="bg-blue-600 h-5 transition-all duration-700"
                  style={{ width: `${(marks / 8) * 100}%` }}
                ></div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}

export default HomePage;

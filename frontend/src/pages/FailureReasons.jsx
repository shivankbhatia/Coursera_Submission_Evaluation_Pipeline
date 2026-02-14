function FailureReasons() {
  return (
    <div className="min-h-screen 
                    bg-gray-100 dark:bg-gray-900 
                    text-gray-800 dark:text-gray-100 
                    transition-colors duration-300 
                    px-4 py-10">

      <div className="max-w-5xl mx-auto 
                      bg-white dark:bg-gray-800 
                      shadow-lg rounded-lg p-8 
                      transition-colors duration-300">

        {/* Page Title */}
        <h4 className="text-2xl md:text-3xl font-bold text-blue-600 mb-8">
          Evaluation Failure Reasons
        </h4>

        {/* ---------------- INVALID SECTION ---------------- */}
        <section className="mb-12">

          <h2 className="text-xl font-semibold text-yellow-600 mb-4">
            INVALID
          </h2>

          <p className="leading-relaxed mb-6 
                        text-gray-700 dark:text-gray-300">
            INVALID means the Coursera certificate link was not provided correctly.
            The link must be the official certificate completion URL issued by Coursera.
            Any other link (profile link, course page, screenshot, etc.) will result in INVALID.
          </p>

          {/* Images Section */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

            {/* Correct Example 1 */}
            <div className="text-center">
              <p className="text-green-600 font-semibold mb-2">
                Correct Example
              </p>
              <img
                src="/images/correct1.png"
                alt="Correct Certificate Example 1"
                className="rounded-lg shadow-md dark:shadow-gray-700 
                           border dark:border-gray-700 
                           w-full object-cover"
              />
            </div>

            {/* Correct Example 2 */}
            <div className="text-center">
              <p className="text-green-600 font-semibold mb-2">
                Correct Example
              </p>
              <img
                src="/images/correct2.png"
                alt="Correct Certificate Example 2"
                className="rounded-lg shadow-md dark:shadow-gray-700 
                           border dark:border-gray-700 
                           w-full object-cover"
              />
            </div>

            {/* Incorrect Example */}
            <div className="text-center">
              <p className="text-red-600 font-semibold mb-2">
                Incorrect Example
              </p>
              <img
                src="/images/incorrect.png"
                alt="Incorrect Certificate Example"
                className="rounded-lg shadow-md dark:shadow-gray-700 
                           border dark:border-gray-700 
                           w-full object-cover"
              />
            </div>

          </div>

        </section>

        {/* Divider */}
        <div className="border-t 
                        border-gray-200 dark:border-gray-700 
                        my-8"></div>

        {/* ---------------- FAIL SECTION ---------------- */}
        <section>

          <h2 className="text-xl font-semibold text-red-600 mb-4">
            FAIL
          </h2>

          <p className="leading-relaxed 
                        text-gray-700 dark:text-gray-300">
            FAIL means that the LinkedIn post does not clearly mention
            or describe the Coursera guided project that was submitted.
            The evaluation system checks whether the project is referenced
            properly. If it is missing, vague, or unrelated,
            the submission will be marked as FAIL.
          </p>

        </section>

      </div>
    </div>
  );
}

export default FailureReasons;

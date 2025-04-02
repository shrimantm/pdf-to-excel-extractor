import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

function App() {
  const [file, setFile] = useState(null)
  const [downloadUrl, setDownloadUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setDownloadUrl('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsLoading(true)
    const formData = new FormData()
    formData.append('pdf_file', file)

    try {
      const response = await axios.post('http://127.0.0.1:5000/', formData, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      setDownloadUrl(url)
    } catch (error) {
      console.error('Error uploading file:', error)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (downloadUrl) {
      const a = document.createElement('a')
      a.href = downloadUrl
      a.download = 'Student_Marks.xlsx'
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      setDownloadUrl('')
    }
  }, [downloadUrl])

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-500">
      <div className="w-full max-w-md mx-auto p-6">
        <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              PDF to Excel Extractor
            </h1>
            <p className="text-gray-600">
              Upload your PDF file to convert it to Excel
            </p>
          </div>

          <form onSubmit={handleUpload} className="space-y-6">
            <div className="flex flex-col items-center p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors">
              <input
                id="pdf_file"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              <label 
                htmlFor="pdf_file" 
                className="cursor-pointer text-center"
              >
                <div className="flex flex-col items-center gap-2">
                  <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span className="text-gray-600">
                    {file ? file.name : 'Drop your PDF here or click to browse'}
                  </span>
                </div>
              </label>
            </div>

            <button
              type="submit"
              disabled={!file || isLoading}
              className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-300
                ${!file || isLoading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg'}`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Processing...
                </div>
              ) : (
                'Convert to Excel'
              )}
            </button>
          </form>

          {downloadUrl && (
            <div className="text-center">
              <a
                href={downloadUrl}
                download="Student_Marks.xlsx"
                className="inline-block w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition duration-300"
              >
                Download Excel File
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default App

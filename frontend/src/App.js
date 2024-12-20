import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [userQuestion, setUserQuestion] = useState('');
  const [pdfFiles, setPdfFiles] = useState(null);
  const [response, setResponse] = useState('');

  const handleFileChange = (e) => {
    setPdfFiles(e.target.files);
  };

  const handleQuestionChange = (e) => {
    setUserQuestion(e.target.value);
  };

  const handleSubmit = async () => {
    if (!userQuestion || !pdfFiles) {
      alert('Please enter a question and upload a PDF file.');
      return;
    }

    // Upload PDF to backend
    const formData = new FormData();
    Array.from(pdfFiles).forEach((file) => formData.append('pdfFiles', file));

    try {
      await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Send question to backend
      const { data } = await axios.post('http://localhost:5000/ask', {
        question: userQuestion,
      });

      setResponse(data.answer);
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while processing your request.');
    }
  };

  return (
    <div className="App">
      <h1>Chat with PDF Using RAG Pipeline</h1>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleFileChange}
      />
      <input
        type="text"
        value={userQuestion}
        onChange={handleQuestionChange}
        placeholder="Ask a question from the PDF"
      />
      <button onClick={handleSubmit}>Submit & Process</button>
      <div className='response'>
        <h3>Response:</h3>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default App;

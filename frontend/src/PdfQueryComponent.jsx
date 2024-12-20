import React, { useState } from 'react';
import axios from 'axios';

const PdfQueryComponent = () => {
  const [pdfFiles, setPdfFiles] = useState([]);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');

  const handleFileChange = (e) => {
    setPdfFiles([...e.target.files]);
  };

  const handleQueryChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async () => {
    const formData = new FormData();
    pdfFiles.forEach((file) => {
      formData.append('pdf_files', file);
    });
  
    try {
      const response = await axios.post('http://localhost:5000/query', {
        pdf_files: pdfFiles,
        query: query,
      });
      setResponse(response.data.response);
    } catch (error) {
      console.error('Error fetching data from backend:', error);
      setResponse('Error fetching data.');
    }
  };

  return (
    <div>
      <h1>PDF Query System</h1>
      <input
        type="file"
        multiple
        accept=".pdf"
        onChange={handleFileChange}
      />
      <textarea
        value={query}
        onChange={handleQueryChange}
        placeholder="Enter your query here"
      />
      <button onClick={handleSubmit}>Submit Query</button>
      {response && <div><h3>Response: {response}</h3></div>}
    </div>
  );
};

export default PdfQueryComponent;

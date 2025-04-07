'use client';

import { useState, useRef } from 'react';
import AnalysisResults from './components/AnalysisResults';
import VisualizationSteps from './components/VisualizationSteps';
import FinalReport from './components/FinalReport';
import ReportModal from './components/ReportModal';

// const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api-auto-viz.100s.site';
const API_URL = 'https://api-auto-viz.100s.site';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [showReport, setShowReport] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const [workspace, setWorkspace] = useState('default');
  const [language, setLanguage] = useState('Chinese');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisData(null);
    setCurrentStep(0);

    const formData = new FormData();
    formData.append('file', file);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(
        `${API_URL}/analyze-dataset?workspace=${workspace}&language=${language}`,
        {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal,
        }
      );

      if (!response.ok) {
        throw new Error('Failed to start analysis');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to read response');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const data = JSON.parse(line);

            switch (data.type) {
              case 'analysis':
                setAnalysisData((prev: any) => ({
                  ...prev,
                  analysis: data.data,
                }));
                setCurrentStep(1);
                break;
              case 'tasks':
                setAnalysisData((prev: any) => ({
                  ...prev,
                  tasks: data.data,
                }));
                setCurrentStep(2);
                break;
              case 'image':
                setAnalysisData((prev: any) => ({
                  ...prev,
                  images: [...(prev?.images || []), data.data],
                }));
                break;
              case 'description':
                setAnalysisData((prev: any) => ({
                  ...prev,
                  descriptions: [...(prev?.descriptions || []), data.data],
                }));
                break;
              case 'final':
                setAnalysisData((prev: any) => ({
                  ...prev,
                  final: data.data,
                }));
                setCurrentStep(3);
                break;
              case 'error':
                setError(data.data);
                break;
            }
          } catch (err) {
            console.error('Error parsing response:', err);
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setError('Analysis was cancelled');
      } else {
        setError('Failed to analyze data');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const stopAnalysis = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsAnalyzing(false);
    }
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">AI Data Analysis</h1>

        <div className="mb-8">
          <div className="flex flex-col gap-4 mb-4">
            <div className="flex items-center gap-4">
              <label className="w-24">Workspace:</label>
              <input
                type="text"
                value={workspace}
                onChange={(e) => setWorkspace(e.target.value)}
                className="border p-2 rounded"
              />
            </div>
            <div className="flex items-center gap-4">
              <label className="w-24">Language:</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="border p-2 rounded"
              >
                <option value="Chinese">Chinese</option>
                <option value="English">English</option>
                {/* 添加更多语言选项 */}
              </select>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
            <button
              onClick={startAnalysis}
              disabled={!file || isAnalyzing}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            >
              Start Analysis
            </button>
            {isAnalyzing && (
              <button
                onClick={stopAnalysis}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Stop Analysis
              </button>
            )}
          </div>
          {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>

        {analysisData && (
          <div className="space-y-8">
            <AnalysisResults data={analysisData.analysis} />
            <VisualizationSteps
              tasks={analysisData.tasks}
              images={analysisData.images}
              descriptions={analysisData.descriptions}
              currentStep={currentStep}
            />
            {analysisData.final && (
              <FinalReport
                data={analysisData.final}
                onShowReport={() => setShowReport(true)}
              />
            )}
          </div>
        )}
      </div>

      {analysisData?.final?.data_analysis_report && (
        <ReportModal
          isOpen={showReport}
          onClose={() => setShowReport(false)}
          reportUrl={analysisData.final.data_analysis_report}
        />
      )}
    </main>
  );

}

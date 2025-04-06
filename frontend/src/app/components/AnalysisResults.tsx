'use client';

interface AnalysisResultsProps {
  data: any;
}

export default function AnalysisResults({ data }: AnalysisResultsProps) {
  if (!data) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Data Analysis Results</h2>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold mb-2">Data Types</h3>
          <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(data.dtypes, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">Sample Data</h3>
          <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(data.sample, null, 2)}
          </pre>
        </div>
        <div>
          <h3 className="text-lg font-semibold mb-2">Detailed Analysis</h3>
          <pre className="bg-gray-50 p-4 rounded-md overflow-x-auto">
            {JSON.stringify(data.analysis, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
} 
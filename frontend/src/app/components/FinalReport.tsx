'use client';

interface FinalReportProps {
  data: {
    analysis: string;
    tasks: string[];
    image_urls: string[];
    descriptions: string[];
    data_analysis_report: string;
  };
  onShowReport: () => void;
}

export default function FinalReport({ data, onShowReport }: FinalReportProps) {
  if (!data) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Final Analysis Report</h2>
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-2">Summary</h3>
          <p className="text-gray-600">{data.analysis}</p>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-2">Visualizations</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.image_urls.map((url, index) => (
              <div key={index} className="border rounded-lg p-4">
                <img
                  src={url}
                  alt={`Visualization ${index + 1}`}
                  className="w-full h-auto rounded-lg"
                />
                {data.descriptions[index] && (
                  <p className="mt-2 text-gray-600">{data.descriptions[index]}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-center">
          <button
            onClick={onShowReport}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            View Full Report
          </button>
        </div>
      </div>
    </div>
  );
} 
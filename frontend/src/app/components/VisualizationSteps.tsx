'use client';

interface VisualizationStepsProps {
  tasks: string[];
  images: Array<{ url: string }>;
  descriptions: Array<{ url: string; description: string }>;
  currentStep: number;
}

export default function VisualizationSteps({
  tasks,
  images,
  descriptions,
  currentStep,
}: VisualizationStepsProps) {
  if (!tasks || !images || !descriptions) return null;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4">Visualization Steps</h2>
      <div className="space-y-6">
        {tasks.map((task, index) => {
          const image = images[index];
          const description = descriptions[index];
          const isActive = index <= currentStep;

          return (
            <div
              key={index}
              className={`border rounded-lg p-4 ${isActive ? 'border-blue-500' : 'border-gray-200'
                }`}
            >
              <div className="flex items-start gap-4">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${isActive ? 'bg-blue-500 text-white' : 'bg-gray-200'
                    }`}
                >
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-2">{task}</h3>
                  {isActive && image && (
                    <div className="mt-4">
                      <img
                        src={image.url}
                        alt={`Visualization step ${index + 1}`}
                        className="max-w-full h-auto rounded-lg shadow-sm"
                      />
                      {description && (
                        <p className="mt-2 text-gray-600">{description.description}</p>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
} 
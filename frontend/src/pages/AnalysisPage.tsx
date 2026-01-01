// Analysis page with dashboard

import { useAnalysisIndex } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';

export function AnalysisPage() {
  const { data: analysisIndex, isLoading, error } = useAnalysisIndex();
  
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load analysis data" />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Job Market Analysis</h1>
      
      {analysisIndex && (
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-primary mb-2">
              {analysisIndex.data_summary.total_jobs.toLocaleString()}
            </div>
            <div className="text-gray-600">Total Jobs</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-secondary mb-2">
              {analysisIndex.data_summary.unique_companies.toLocaleString()}
            </div>
            <div className="text-gray-600">Companies</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-accent mb-2">
              {analysisIndex.data_summary.unique_skills.toLocaleString()}
            </div>
            <div className="text-gray-600">Unique Skills</div>
          </div>
        </div>
      )}
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-semibold mb-4">Available Analyses</h2>
        <p className="text-gray-600">Analysis visualizations will be implemented here.</p>
        
        {analysisIndex && (
          <ul className="mt-4 space-y-2">
            {analysisIndex.available_analyses.map((analysis) => (
              <li key={analysis.id} className="p-3 border rounded hover:bg-gray-50">
                <div className="font-semibold">{analysis.title}</div>
                {analysis.last_updated && (
                  <div className="text-sm text-gray-500">
                    Updated: {new Date(analysis.last_updated).toLocaleDateString()}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

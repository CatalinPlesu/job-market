// Home page component

import { Link } from 'react-router-dom';
import { useJobsIndex } from '../api/hooks';
import { Loading } from '../components/common/Loading';

export function HomePage() {
  const { data: index, isLoading } = useJobsIndex();
  
  if (isLoading) return <Loading />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Moldova Job Market
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Explore {index?.total_jobs.toLocaleString() || '0'} job opportunities across all industries
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/jobs"
              className="px-8 py-3 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors text-lg font-semibold"
            >
              Browse Jobs
            </Link>
            <Link
              to="/analysis"
              className="px-8 py-3 bg-white text-primary border-2 border-primary rounded-lg hover:bg-blue-50 transition-colors text-lg font-semibold"
            >
              View Analysis
            </Link>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-primary mb-2">
              {index?.total_jobs.toLocaleString() || '0'}
            </div>
            <div className="text-gray-600">Total Jobs</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-secondary mb-2">
              {index?.metadata.companies.length || '0'}
            </div>
            <div className="text-gray-600">Companies</div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-accent mb-2">
              {index?.metadata.job_functions.length || '0'}
            </div>
            <div className="text-gray-600">Job Functions</div>
          </div>
        </div>
        
        <div className="bg-blue-50 p-8 rounded-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-lg mb-2">Comprehensive Filtering</h3>
              <p className="text-gray-600">
                Filter jobs by 50+ criteria including skills, location, salary, and more
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Market Analysis</h3>
              <p className="text-gray-600">
                Interactive charts and visualizations showing salary trends and market insights
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Detailed Job Info</h3>
              <p className="text-gray-600">
                View both structured parsed data and original job postings
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-lg mb-2">Daily Updates</h3>
              <p className="text-gray-600">
                Fresh job listings updated daily from multiple sources
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

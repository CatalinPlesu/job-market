// Jobs page with browsing and filtering

import { useState } from 'react';
import { useJobsIndex, useJobsPage } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';

export function JobsPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const { data: index, isLoading: indexLoading, error: indexError } = useJobsIndex();
  const { data: page, isLoading: pageLoading, error: pageError } = useJobsPage(currentPage);
  
  if (indexLoading) return <Loading />;
  if (indexError) return <ErrorMessage message="Failed to load job index" />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Browse Jobs</h1>
      
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <p className="text-gray-700">
          Showing page {currentPage} of {index?.total_pages || 0} ({index?.total_jobs.toLocaleString() || 0} total jobs)
        </p>
      </div>
      
      {/* TODO: Add filters here */}
      
      {pageLoading ? (
        <Loading />
      ) : pageError ? (
        <ErrorMessage message="Failed to load jobs" />
      ) : (
        <div>
          <div className="grid grid-cols-1 gap-4 mb-6">
            {page?.jobs.map((job) => (
              <div key={job.id} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h3>
                <p className="text-gray-600 mb-2">{job.company}</p>
                <div className="flex flex-wrap gap-2 text-sm text-gray-500">
                  {job.location.city && <span>📍 {job.location.city}</span>}
                  {job.seniority_level && <span>👔 {job.seniority_level}</span>}
                  {job.salary && (
                    <span>
                      💰 {job.salary.min?.toLocaleString()}-{job.salary.max?.toLocaleString()} {job.salary.currency}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {/* Pagination */}
          <div className="flex justify-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 bg-white border rounded-md disabled:opacity-50 hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">
              Page {currentPage} of {index?.total_pages || 0}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(index?.total_pages || p, p + 1))}
              disabled={currentPage === (index?.total_pages || 0)}
              className="px-4 py-2 bg-white border rounded-md disabled:opacity-50 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

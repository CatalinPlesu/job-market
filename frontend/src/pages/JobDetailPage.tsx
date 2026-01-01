// Job detail page

import { useParams } from 'react-router-dom';
import { useJobDetail } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';

export function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const { data: jobDetail, isLoading, error } = useJobDetail(Number(jobId));
  
  if (isLoading) return <Loading />;
  if (error || !jobDetail) return <ErrorMessage message="Failed to load job details" />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{jobDetail.job.title}</h1>
        <p className="text-xl text-gray-600 mb-6">{jobDetail.job.parsed.company}</p>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">Job Details</h2>
          <p className="text-gray-600">
            Full job detail view with parsed and raw tabs will be implemented here.
          </p>
        </div>
      </div>
    </div>
  );
}

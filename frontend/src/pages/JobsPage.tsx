// Jobs page with browsing and filtering

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useJobsIndex, useJobsPage } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { MapPin, Briefcase, DollarSign, ChevronLeft, ChevronRight } from 'lucide-react';

export function JobsPage() {
  const [currentPage, setCurrentPage] = useState(1);
  const { data: index, isLoading: indexLoading, error: indexError } = useJobsIndex();
  const { data: page, isLoading: pageLoading, error: pageError } = useJobsPage(currentPage);
  
  if (indexLoading) return <Loading />;
  if (indexError) return <ErrorMessage message="Failed to load job index" />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Browse Jobs</h1>
        <p className="text-muted-foreground">
          Discover opportunities across Moldova
        </p>
      </div>
      
      <div className="mb-6">
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                Page {currentPage} of {index?.total_pages || 0}
              </span>
              <span className="font-medium">
                {index?.total_jobs.toLocaleString() || 0} total jobs
              </span>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* TODO: Add filters here */}
      
      {pageLoading ? (
        <Loading />
      ) : pageError ? (
        <ErrorMessage message="Failed to load jobs" />
      ) : (
        <div>
          <div className="grid grid-cols-1 gap-4 mb-8">
            {page?.jobs.map((job) => (
              <Card key={job.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-2xl mb-2 hover:text-primary transition-colors">
                        <Link to={`/jobs/${job.id}`}>{job.title}</Link>
                      </CardTitle>
                      <CardDescription className="text-base">
                        {job.company}
                      </CardDescription>
                    </div>
                    {job.seniority_level && (
                      <Badge variant="secondary" className="ml-4">
                        {job.seniority_level}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                    {job.location.city && (
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        <span>{job.location.city}</span>
                      </div>
                    )}
                    {job.job_function && (
                      <div className="flex items-center gap-1">
                        <Briefcase className="w-4 h-4" />
                        <span>{job.job_function}</span>
                      </div>
                    )}
                    {job.salary && (
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-4 h-4" />
                        <span>
                          {job.salary.min?.toLocaleString()}-{job.salary.max?.toLocaleString()} {job.salary.currency}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  {job.requirements.hard_skills.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {job.requirements.hard_skills.slice(0, 5).map((skill, idx) => (
                        <Badge key={idx} variant="outline">
                          {skill}
                        </Badge>
                      ))}
                      {job.requirements.hard_skills.length > 5 && (
                        <Badge variant="outline">
                          +{job.requirements.hard_skills.length - 5} more
                        </Badge>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* Pagination */}
          <div className="flex items-center justify-center gap-2">
            <Button
              variant="outline"
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
            <div className="px-4 py-2 text-sm text-muted-foreground">
              Page {currentPage} of {index?.total_pages || 0}
            </div>
            <Button
              variant="outline"
              onClick={() => setCurrentPage(p => Math.min(index?.total_pages || p, p + 1))}
              disabled={currentPage === (index?.total_pages || 0)}
            >
              Next
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

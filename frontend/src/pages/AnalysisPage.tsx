// Analysis page with dashboard

import { useAnalysisIndex } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { TrendingUp, Users, Briefcase, Clock } from 'lucide-react';

export function AnalysisPage() {
  const { data: analysisIndex, isLoading, error } = useAnalysisIndex();
  
  if (isLoading) return <Loading />;
  if (error) return <ErrorMessage message="Failed to load analysis data" />;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Market Analysis</h1>
        <p className="text-muted-foreground">
          Comprehensive insights into Moldova's job market
        </p>
      </div>
      
      {analysisIndex && (
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardDescription>Total Jobs</CardDescription>
                <Briefcase className="w-5 h-5 text-muted-foreground" />
              </div>
              <CardTitle className="text-3xl">
                {analysisIndex.data_summary.total_jobs.toLocaleString()}
              </CardTitle>
            </CardHeader>
          </Card>
          
          <Card className="border-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardDescription>Companies</CardDescription>
                <Users className="w-5 h-5 text-muted-foreground" />
              </div>
              <CardTitle className="text-3xl">
                {analysisIndex.data_summary.unique_companies.toLocaleString()}
              </CardTitle>
            </CardHeader>
          </Card>
          
          <Card className="border-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardDescription>Unique Skills</CardDescription>
                <TrendingUp className="w-5 h-5 text-muted-foreground" />
              </div>
              <CardTitle className="text-3xl">
                {analysisIndex.data_summary.unique_skills.toLocaleString()}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>
      )}
      
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">Available Analyses</CardTitle>
          <CardDescription>
            Interactive visualizations and insights (coming soon)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {analysisIndex && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysisIndex.available_analyses.map((analysis) => (
                <Card key={analysis.id} className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{analysis.title}</CardTitle>
                        {analysis.last_updated && (
                          <CardDescription className="flex items-center gap-1 mt-2">
                            <Clock className="w-3 h-3" />
                            Updated: {new Date(analysis.last_updated).toLocaleDateString()}
                          </CardDescription>
                        )}
                      </div>
                      {analysis.temporal && (
                        <span className="text-xs bg-accent/10 text-accent px-2 py-1 rounded">
                          Time Series
                        </span>
                      )}
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

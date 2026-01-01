// Home page component

import { Link } from 'react-router-dom';
import { useJobsIndex } from '../api/hooks';
import { Loading } from '../components/common/Loading';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Briefcase, TrendingUp, Filter, Clock, BarChart3, Users } from 'lucide-react';

export function HomePage() {
  const { data: index, isLoading } = useJobsIndex();
  
  if (isLoading) return <Loading />;
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/20">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Explore Moldova's
            <span className="text-primary"> Job Market</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            Discover {index?.total_jobs.toLocaleString() || '0'} job opportunities across all industries with powerful filtering and market analytics
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link to="/jobs">
              <Button size="lg">
                <Briefcase className="mr-2 h-5 w-5" />
                Browse Jobs
              </Button>
            </Link>
            <Link to="/analysis">
              <Button size="lg" variant="outline">
                <BarChart3 className="mr-2 h-5 w-5" />
                View Analysis
              </Button>
            </Link>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
            <Card className="border-2 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="text-3xl font-bold text-primary">
                  {index?.total_jobs.toLocaleString() || '0'}
                </CardTitle>
                <CardDescription>Total Jobs Available</CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="border-2 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="text-3xl font-bold text-secondary">
                  {index?.metadata.companies.length || '0'}
                </CardTitle>
                <CardDescription>Active Companies</CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="border-2 hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <CardTitle className="text-3xl font-bold text-accent">
                  {index?.metadata.job_functions.length || '0'}
                </CardTitle>
                <CardDescription>Job Categories</CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </div>
      
      {/* Features Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Powerful Features</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Filter className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-xl">Advanced Filtering</CardTitle>
                <CardDescription>
                  Filter jobs by 50+ criteria including skills, location, salary, experience level, and much more
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-secondary" />
                </div>
                <CardTitle className="text-xl">Market Analytics</CardTitle>
                <CardDescription>
                  Interactive charts and visualizations showing salary trends, skill demand, and market insights
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                  <Briefcase className="w-6 h-6 text-accent" />
                </div>
                <CardTitle className="text-xl">Detailed Job Info</CardTitle>
                <CardDescription>
                  View both structured parsed data and original job postings with full transparency
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-orange-500/10 flex items-center justify-center mb-4">
                  <Clock className="w-6 h-6 text-orange-500" />
                </div>
                <CardTitle className="text-xl">Daily Updates</CardTitle>
                <CardDescription>
                  Fresh job listings updated daily from multiple sources across Moldova
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-blue-500" />
                </div>
                <CardTitle className="text-xl">Smart Insights</CardTitle>
                <CardDescription>
                  Hierarchical filtering that adapts as you select criteria for smarter job discovery
                </CardDescription>
              </CardHeader>
            </Card>
            
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-green-500" />
                </div>
                <CardTitle className="text-xl">All Industries</CardTitle>
                <CardDescription>
                  Coverage across technology, healthcare, manufacturing, retail, and many more sectors
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </div>
      
      {/* CTA Section */}
      <div className="container mx-auto px-4 py-16">
        <Card className="max-w-4xl mx-auto border-2 bg-primary/5">
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to Find Your Next Opportunity?</h2>
            <p className="text-muted-foreground mb-6 text-lg">
              Start exploring {index?.total_jobs.toLocaleString() || '0'} jobs with our powerful search and filtering tools
            </p>
            <Link to="/jobs">
              <Button size="lg">
                Get Started
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

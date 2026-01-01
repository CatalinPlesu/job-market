// Header component with navigation

import { Link } from 'react-router-dom';
import { Briefcase, Menu } from 'lucide-react';
import { Button } from '../ui/Button';

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 transition-opacity hover:opacity-80">
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary text-primary-foreground">
              <Briefcase className="w-6 h-6" />
            </div>
            <div className="flex flex-col">
              <span className="text-xl font-bold">Job Market</span>
              <span className="text-xs text-muted-foreground">Moldova</span>
            </div>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-2">
            <Link to="/">
              <Button variant="ghost">Home</Button>
            </Link>
            <Link to="/jobs">
              <Button variant="ghost">Browse Jobs</Button>
            </Link>
            <Link to="/analysis">
              <Button variant="ghost">Analysis</Button>
            </Link>
          </nav>
          
          {/* Mobile menu button */}
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="w-5 h-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}

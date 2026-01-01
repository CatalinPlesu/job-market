// Footer component

export function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-gray-100 border-t mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">About</h3>
            <p className="text-sm text-gray-600">
              Job Market Moldova provides insights and analytics for the Moldovan job market.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Resources</h3>
            <ul className="space-y-1 text-sm text-gray-600">
              <li><a href="#" className="hover:text-primary">About</a></li>
              <li><a href="#" className="hover:text-primary">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary">Terms of Service</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">Contact</h3>
            <p className="text-sm text-gray-600">
              Data updated daily from multiple job boards.
            </p>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t text-center text-sm text-gray-500">
          © {currentYear} Job Market Moldova. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

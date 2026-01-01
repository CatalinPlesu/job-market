# Job Market Moldova - Frontend SPA

React-based single-page application for browsing and analyzing the Moldova job market.

## Features

- **Job Browsing**: Browse paginated job listings with comprehensive details
- **Advanced Filtering**: Filter by 50+ criteria including job function, skills, location, salary, and more
- **Hierarchical Filtering**: Dynamic cascading filters (industry → department → job family → specialization)
- **Job Details**: View both parsed structured data and original job postings
- **Market Analysis**: Interactive charts and visualizations showing market trends
- **Mobile Responsive**: Optimized for all screen sizes

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast build and dev experience
- **React Router** for client-side routing
- **TanStack Query** for data fetching and caching
- **Tailwind CSS** for styling
- **Recharts** for data visualizations
- **Headless UI** for accessible components

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:5173/

### Building for Production

Build the application:

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
src/
├── api/                  # API client and React Query hooks
│   ├── client.ts        # Fetch utilities and API endpoints
│   ├── hooks.ts         # React Query hooks
│   └── types.ts         # TypeScript interfaces
├── components/          # React components
│   ├── common/          # Shared components (Header, Footer, Loading, etc.)
│   ├── jobs/            # Job-related components
│   ├── analysis/        # Analysis dashboard components
│   └── charts/          # Chart components
├── pages/               # Page components (routing)
│   ├── HomePage.tsx
│   ├── JobsPage.tsx
│   ├── JobDetailPage.tsx
│   └── AnalysisPage.tsx
├── hooks/               # Custom React hooks
├── context/             # React Context providers
├── utils/               # Utility functions
├── App.tsx              # Main app component with routing
└── main.tsx             # Application entry point
```

## API Endpoints

The application expects the following API structure:

- `/api/jobs/index.json` - Job metadata and filtering information
- `/api/jobs/page-{N}.json` - Paginated job listings
- `/api/jobs/{id}/detail.json` - Individual job details
- `/api/analysis/index.json` - Available analyses
- `/api/analysis/{analysis-id}.json` - Individual analysis data

Mock data is provided in `public/api/` for development.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Part of the Job Market Moldova project.

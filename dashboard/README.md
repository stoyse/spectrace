# SpecTrace Dashboard

> AI-Powered Firmware Analysis Platform

SpecTrace is an advanced firmware security analysis platform that leverages cutting-edge AI algorithms to analyze and compare firmware code, detect anomalies, and provide comprehensive security insights.

## 🚀 Features

- **AI-Powered Analysis**: Advanced algorithms compare code changes and analyze specifications
- **Security Compliance**: Automated validation of security compliance standards  
- **Intuitive Interface**: Modern, responsive dashboard built with React and TypeScript
- **Real-time Progress**: Live progress tracking during analysis operations
- **Multi-file Support**: Upload and compare multiple firmware files and specifications
- **Comprehensive Reports**: Detailed analysis results with actionable recommendations

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + shadcn/ui
- **Icons**: Lucide React
- **Routing**: React Router Dom
- **State Management**: TanStack Query
- **Form Handling**: React Hook Form + Zod
- **File Upload**: React Dropzone
- **Charts**: Recharts
- **Notifications**: Sonner

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn or bun
- Backend API server running on `http://localhost:8000`

## 🚀 Getting Started

### Installation

1. Clone the repository:
```bash
git clone <YOUR_GIT_URL>
cd dashboard
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or  
bun install
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
# or
bun dev
```

4. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🎯 Usage

### 1. Upload Files
- Navigate to the dashboard (`/dashboard`)
- Upload your original firmware code files (.asm, .c, .h)
- Upload your original specification files (.txt, .md)
- Upload your updated firmware code files
- Upload your updated specification files

### 2. AI Analysis
The platform will automatically:
- Compare code changes between versions
- Analyze specification updates
- Validate security compliance
- Generate comprehensive results

### 3. Get Results
Receive detailed insights including:
- Security vulnerability assessments
- Code change analysis
- Compliance validation reports
- Actionable recommendations

## 🏗️ Project Structure

```
dashboard/
├── public/                 # Static assets
│   ├── android-chrome-*.png # App icons/logos
│   ├── favicon.*           # Favicon files
│   └── robots.txt         
├── src/
│   ├── components/
│   │   └── ui/            # Reusable UI components
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility functions
│   ├── pages/             # Page components
│   │   ├── Dashboard.tsx  # Main analysis dashboard
│   │   ├── Index.tsx      # Landing page
│   │   └── NotFound.tsx   # 404 page
│   ├── App.tsx            # Main app component
│   ├── main.tsx          # App entry point
│   └── index.css         # Global styles
├── package.json          # Dependencies and scripts
├── tailwind.config.ts    # Tailwind configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## 🔧 Configuration

### Backend API Endpoints

The dashboard expects the following API endpoints to be available:

- `POST /api/v1/compare-code` - Compare firmware code files
- `POST /api/v1/compare-specs` - Compare specification files  
- `POST /api/v1/validate-compliance` - Validate security compliance

### Environment Variables

Create a `.env` file if you need to customize the API base URL:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🎨 Customization

### Theming

The project uses Tailwind CSS with a custom theme. Colors and styling can be customized in:
- `tailwind.config.ts` - Tailwind configuration
- `src/index.css` - CSS variables for theme colors

### Components

All UI components are built with Radix UI and can be customized in the `src/components/ui/` directory.

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory, ready to be deployed to any static hosting service.

### Deployment Options

- **Vercel**: Connect your Git repository for automatic deployments
- **Netlify**: Drag and drop the `dist` folder or connect via Git
- **GitHub Pages**: Use GitHub Actions to deploy automatically
- **Static Hosting**: Upload `dist` folder to any static hosting service

## 📱 Pages

- **Landing Page** (`/`) - Introduction and overview of SpecTrace features
- **Dashboard** (`/dashboard`) - Main analysis interface for uploading and analyzing firmware
- **404 Page** (`*`) - Not found page for invalid routes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of the AI Cybersecurity Hackathon sponsored by SAP & KPMG.

## 📧 Support

For questions or support, please contact the development team.

---

**SpecTrace Dashboard** - Revolutionizing Firmware Security with AI
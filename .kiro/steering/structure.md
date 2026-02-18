# Project Structure

## Root Directory
- `src/` - All source code
- `public/` - Static assets (served by Vite)
- Configuration files: `vite.config.js`, `tailwind.config.js`, `postcss.config.js`
- `package.json` - Dependencies and scripts
- `index.html` - Entry point HTML file

## Source Code Organization (`src/`)

### Main Application Files
- `index.jsx` - React app entry point with StrictMode
- `App.jsx` - Main app component with routing setup
- `styles/global.css` - Global Tailwind CSS imports

### Component Architecture
```
src/components/
├── common/          # Shared layout components
│   ├── Header.jsx   # Site navigation
│   ├── Footer.jsx   # Site footer
│   └── Card.jsx     # Reusable card component
├── ui/              # Reusable UI components
│   ├── Modal.jsx    # Modal dialog component
│   └── Dropdown.jsx # Dropdown menu component
├── ChatInterface.jsx # Chat functionality
├── Message.jsx      # Message display component
└── NewsItem.jsx     # News article component
```

### Page Components (`src/pages/`)
- `Home.jsx` - Landing page with hero, features, pricing, testimonials
- `About.jsx` - About page
- `Products.jsx` - Products/services page
- `NotFound.jsx` - 404 error page

### Assets (`src/assets/`)
- `backgroundImage.jpg` - Hero section background
- `productImage.jpg` - Product imagery

## Routing Structure
- `/` - Home page (main landing page)
- `/about` - About page
- `/products` - Products page
- `*` - 404 Not Found page

## Component Conventions
- Use functional components with hooks
- Import React explicitly in each component
- Export components as default exports
- Use JSX file extension for React components
- Organize imports: React first, then third-party, then local imports

## Styling Conventions
- Tailwind CSS utility classes for all styling
- Responsive design with mobile-first approach
- Consistent color scheme (blue-600 primary, gray tones)
- Component-level styling using className prop
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { ToastContainer } from 'react-toastify';
import styled, { createGlobalStyle } from 'styled-components';
import Header from './components/Layout/Header';
import ProtectedRoute from './components/ProtectedRoute';

// Import des composants
import HomePage from './pages/HomePage';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailPage from './pages/ProjectDetailPage';
import StatisticsPage from './pages/StatisticsPage';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';

// Import des styles
import 'react-toastify/dist/ReactToastify.css';
// import 'leaflet/dist/leaflet.css';

// Configuration React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

// Styles globaux
const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background-color: #f8fafc;
    color: #1e293b;
    line-height: 1.5;
  }

  #root {
    min-height: 100vh;
  }
`;

const AppContainer = styled.div`
  min-height: 100vh;
   width: 100%;
  display: flex;
  flex-direction: column;
`;

const MainContent = styled.main`
  flex: 1;
  padding-top: 0;
`;

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <GlobalStyle />
        <AppContainer>
          <Routes>
            {/* Route de login sans header */}
            <Route path="/login" element={<LoginPage />} />
            
            {/* Routes avec header */}
            <Route path="/*" element={
              <>
                <Header />
                <MainContent>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/projects" element={<ProjectsPage />} />
                    <Route path="/projects/:id" element={<ProjectDetailPage />} />
                    <Route path="/statistics" element={<StatisticsPage />} />
                    
                    {/* Route protégée */}
                    <Route 
                      path="/admin" 
                      element={
                        <ProtectedRoute>
                          <AdminPage />
                        </ProtectedRoute>
                      } 
                    />
                    
                    <Route path="*" element={<NotFoundPage />} />
                  </Routes>
                </MainContent>
              </>
            } />
          </Routes>

          {/* Toast notifications */}
          <ToastContainer
            position="bottom-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
          />
        </AppContainer>
      </Router>
      
      {/* {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />} */}
    </QueryClientProvider>
  );
}

export default App;

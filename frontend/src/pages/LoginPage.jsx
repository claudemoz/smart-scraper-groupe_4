import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FiUser, FiLock, FiEye, FiEyeOff, FiLogIn } from 'react-icons/fi';
import { useAuth } from '../hooks/useApi';

const Container = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
`;

const LoginCard = styled.div`
  background: white;
  border-radius: 1rem;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 2rem;
`;

const Logo = styled.div`
  font-size: 2rem;
  margin-bottom: 1rem;
`;

const Title = styled.h1`
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.5rem;
`;

const Subtitle = styled.p`
  color: #64748b;
  font-size: 0.9rem;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const InputGroup = styled.div`
  position: relative;
`;

const InputLabel = styled.label`
  display: block;
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
`;

const InputWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const Input = styled.input`
  width: 100%;
  padding: 0.75rem 1rem;
  padding-left: 2.5rem;
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.3s ease;
  background: white;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }
`;

const InputIcon = styled.div`
  position: absolute;
  left: 0.75rem;
  color: #9ca3af;
  z-index: 1;
`;

const PasswordToggle = styled.button`
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  
  &:hover {
    color: #667eea;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.875rem 1rem;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #dc2626;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  margin-top: 1rem;
  border: 1px solid #fecaca;
`;

const InfoBox = styled.div`
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  color: #0369a1;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1.5rem;
  font-size: 0.9rem;
  text-align: center;
`;

const DemoCredentials = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
  font-size: 0.85rem;
`;

const CredentialItem = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const LoadingSpinner = styled.div`
  width: 20px;
  height: 20px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});
  
  const { login, isLoading, error, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Redirection si déjà authentifié
  useEffect(() => {
    if (isAuthenticated) {
      const from = location.state?.from?.pathname || '/';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Effacer l'erreur de validation pour ce champ
    if (validationErrors[name]) {
      setValidationErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.username.trim()) {
      errors.username = 'Le nom d\'utilisateur est requis';
    }
    
    if (!formData.password.trim()) {
      errors.password = 'Le mot de passe est requis';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    login(formData);
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const fillDemoCredentials = () => {
    setFormData({
      username: 'admin',
      password: 'admin123'
    });
  };

  return (
    <Container>
      <LoginCard>
        <Header>
          <Logo>🏗️</Logo>
          <Title>Connexion</Title>
          <Subtitle>Accédez au tableau de bord administrateur</Subtitle>
        </Header>

        <Form onSubmit={handleSubmit}>
          <InputGroup>
            <InputLabel htmlFor="username">Nom d'utilisateur</InputLabel>
            <InputWrapper>
              <InputIcon>
                <FiUser size={18} />
              </InputIcon>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="Entrez votre nom d'utilisateur"
                value={formData.username}
                onChange={handleInputChange}
                disabled={isLoading}
              />
            </InputWrapper>
            {validationErrors.username && (
              <ErrorMessage>{validationErrors.username}</ErrorMessage>
            )}
          </InputGroup>

          <InputGroup>
            <InputLabel htmlFor="password">Mot de passe</InputLabel>
            <InputWrapper>
              <InputIcon>
                <FiLock size={18} />
              </InputIcon>
              <Input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Entrez votre mot de passe"
                value={formData.password}
                onChange={handleInputChange}
                disabled={isLoading}
              />
              <PasswordToggle
                type="button"
                onClick={togglePasswordVisibility}
                disabled={isLoading}
              >
                {showPassword ? <FiEyeOff size={18} /> : <FiEye size={18} />}
              </PasswordToggle>
            </InputWrapper>
            {validationErrors.password && (
              <ErrorMessage>{validationErrors.password}</ErrorMessage>
            )}
          </InputGroup>

          <SubmitButton type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <LoadingSpinner />
                Connexion en cours...
              </>
            ) : (
              <>
                <FiLogIn size={18} />
                Se connecter
              </>
            )}
          </SubmitButton>

          {error && (
            <ErrorMessage>
              {error.response?.data?.error?.message || error.message || 'Erreur de connexion'}
            </ErrorMessage>
          )}
        </Form>

        <InfoBox>
          Connectez-vous pour accéder aux fonctionnalités d'administration et de gestion du scraper.
        </InfoBox>

        <DemoCredentials>
          <div style={{ fontWeight: '600', marginBottom: '0.5rem', color: '#374151' }}>
            Identifiants de démonstration :
          </div>
          <CredentialItem>
            <span>Nom d'utilisateur :</span>
            <strong>admin</strong>
          </CredentialItem>
          <CredentialItem>
            <span>Mot de passe :</span>
            <strong>admin123</strong>
          </CredentialItem>
          <button
            type="button"
            onClick={fillDemoCredentials}
            style={{
              background: 'none',
              border: '1px solid #d1d5db',
              color: '#667eea',
              padding: '0.5rem 1rem',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontSize: '0.8rem',
              marginTop: '0.5rem',
              width: '100%'
            }}
          >
            Remplir automatiquement
          </button>
        </DemoCredentials>
      </LoginCard>
    </Container>
  );
};

export default LoginPage; 
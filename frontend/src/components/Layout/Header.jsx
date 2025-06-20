import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { FiHome, FiMap, FiBarChart, FiSettings, FiUser, FiLogOut } from 'react-icons/fi';
import { useAuth } from '../../hooks/useApi';

const HeaderContainer = styled.header`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const HeaderContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
`;

const Logo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: white;
`;

const Navigation = styled.nav`
  display: flex;
  gap: 2rem;
  align-items: center;

  @media (max-width: 768px) {
    display: none;
  }
`;

const NavLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  transition: all 0.3s ease;
  font-weight: 500;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-1px);
  }

  &.active {
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2rem;
  font-size: 0.9rem;
`;

const LogoutButton = styled.button`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-1px);
  }
`;

const MobileMenuButton = styled.button`
  display: none;
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;

  @media (max-width: 768px) {
    display: block;
  }
`;

const Header = () => {
  const location = useLocation();
  const { isAuthenticated, logout } = useAuth();

  const navigationItems = [
    { path: '/', label: 'Accueil', icon: FiHome },
    { path: '/projects', label: 'Projets', icon: FiMap },
    { path: '/statistics', label: 'Statistiques', icon: FiBarChart },
    ...(isAuthenticated ? [{ path: '/admin', label: 'Administration', icon: FiSettings }] : [])
  ];

  const isActivePath = (path) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <HeaderContainer>
      <HeaderContent>
        <Logo as={Link} to="/">
          🏗️ Paris se Transforme
        </Logo>

        <Navigation>
          {navigationItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={isActivePath(item.path) ? 'active' : ''}
              >
                <IconComponent size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </Navigation>

        <UserSection>
          {isAuthenticated ? (
            <>
              <UserInfo>
                <FiUser size={16} />
                Admin
              </UserInfo>
              <LogoutButton onClick={logout}>
                <FiLogOut size={16} />
                Déconnexion
              </LogoutButton>
            </>
          ) : (
            <NavLink to="/login">
              <FiUser size={16} />
              Connexion
            </NavLink>
          )}
        </UserSection>

        <MobileMenuButton>
          ☰
        </MobileMenuButton>
      </HeaderContent>
    </HeaderContainer>
  );
};

export default Header; 
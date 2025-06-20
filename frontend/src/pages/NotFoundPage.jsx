import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
  padding-top: 4rem;
`;

const NotFoundPage = () => {
  return (
    <Container>
      <h1>404 - Page non trouvée</h1>
      <p>La page que vous recherchez n'existe pas.</p>
      <Link to="/">Retour à l'accueil</Link>
    </Container>
  );
};

export default NotFoundPage; 
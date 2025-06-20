import React from 'react';
import { useParams } from 'react-router-dom';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
`;

const ProjectDetailPage = () => {
  const { id } = useParams();

  return (
    <Container>
      <h1>Détail du projet {id}</h1>
      <p>Page en cours de développement...</p>
    </Container>
  );
};

export default ProjectDetailPage; 